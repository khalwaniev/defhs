#!/usr/bin/env python3
"""Concurrent, resumable download of one completed Wave1 output package.

Run with the installed Kaggle CLI's Python environment. Signed artifact URLs
remain in memory and are never written to logs or provenance.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests
from kaggle.api.kaggle_api_extended import KaggleApi, ApiListKernelSessionOutputRequest

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1<<20),b''):h.update(chunk)
    return h.hexdigest()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('kernel');parser.add_argument('destination',type=Path)
    parser.add_argument('--expected-source',required=True)
    args=parser.parse_args();owner,slug=args.kernel.split('/')
    api=KaggleApi();api.authenticate();index={};token=None
    with api.build_kaggle_client() as client:
        while True:
            request=ApiListKernelSessionOutputRequest()
            request.user_name=owner;request.kernel_slug=slug;request.page_size=20
            if token:request.page_token=token
            response=client.kernels.kernels_api_client.list_kernel_session_output(request)
            for item in response.files or []:
                assert item.file_name not in index
                index[item.file_name]=item.url
            token=response.next_page_token
            if not token:break
    prefix='rs_system3_wave1_001/'
    manifest_name=prefix+'SHA256_MANIFEST.json'
    assert manifest_name in index,'Completed package manifest is unavailable.'
    def fetch(name,expected=None):
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        assert 'PROTECTED' not in name.upper() and 'VALIDATION_VP' not in name.upper()
        target=args.destination/relative
        if expected and target.is_file() and target.stat().st_size==expected['bytes'] and digest(target)==expected['sha256']:
            return 'REUSED',name
        target.parent.mkdir(parents=True,exist_ok=True)
        temporary=target.with_name(target.name+'.download')
        for attempt in range(3):
            try:
                with requests.get(index[name],stream=True,timeout=(30,180)) as response:
                    response.raise_for_status()
                    h=hashlib.sha256();size=0
                    with temporary.open('wb') as stream:
                        for chunk in response.iter_content(1<<20):
                            if chunk:stream.write(chunk);h.update(chunk);size+=len(chunk)
                if expected:
                    assert size==expected['bytes'] and h.hexdigest()==expected['sha256'],f'Byte integrity mismatch: {name}'
                temporary.replace(target)
                return 'DOWNLOADED',name
            except requests.RequestException as error:
                if attempt==2:
                    # Requests exceptions can include the signed URL.
                    status=getattr(getattr(error,'response',None),'status_code',None)
                    raise RuntimeError(f'{name}: {type(error).__name__}; HTTP status {status}') from None
                time.sleep(attempt+1)
        raise AssertionError(name)
    fetch(manifest_name)
    authority=json.loads((args.destination/manifest_name).read_text())
    expected={prefix+item['path']:item for item in authority['files']}
    assert len(expected)==len(authority['files']) and set(expected)<=set(index)
    provenance_name=prefix+'GPU_EXECUTION_PROVENANCE.json'
    fetch(provenance_name,expected[provenance_name])
    provenance=json.loads((args.destination/provenance_name).read_text())
    assert provenance['source_sha']==args.expected_source
    print(json.dumps({'files':len(expected),'bytes':sum(x['bytes'] for x in expected.values()),
                      'source_sha':provenance['source_sha']},indent=2),flush=True)
    counts={'REUSED':0,'DOWNLOADED':0}
    with ThreadPoolExecutor(max_workers=4) as pool:
        pending=[pool.submit(fetch,name,record) for name,record in expected.items()]
        for task in as_completed(pending):
            result,name=task.result();counts[result]+=1
            print(f'{result} {name}',flush=True)
    print(json.dumps({'status':'COMPLETE_SHA256_VERIFIED','counts':counts,
                      'manifest_sha256':digest(args.destination/manifest_name)},indent=2),flush=True)

if __name__=='__main__':main()
