#!/usr/bin/env python3
"""Kaggle two-T4 extraction only; no heads, protected data or submission API."""
from __future__ import annotations
import base64, gzip, hashlib, importlib.metadata, json, multiprocessing as mp
import os, random, subprocess, sys, time, traceback, urllib.request
from pathlib import Path

PAYLOAD = {}  # Replaced by the package builder with the exact small input contract.
OUT = Path('/kaggle/working/rs_defhs_score_push_001_audio')
INPUT = Path('/kaggle/input')
SEED = 20261001


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def dump(p, x):
    p.write_text(json.dumps(x, indent=2, ensure_ascii=False) + '\n')


def checkpoint(name):
    spec = PAYLOAD['models'][name]
    root = Path('/tmp/defhs_score_push_models') / name
    root.mkdir(parents=True, exist_ok=True)
    for file, obj in spec['files'].items():
        p = root / file
        if not p.exists():
            url = f"https://modelscope.cn/api/v1/models/{spec['model_id']}/repo?Revision={obj['Revision']}&FilePath={file}"
            with urllib.request.urlopen(url, timeout=180) as response, p.open('wb') as f:
                while True:
                    b = response.read(1 << 20)
                    if not b: break
                    f.write(b)
        assert p.stat().st_size == obj['Size'] and sha(p) == obj['Sha256'], p
    dump(OUT / f'{name}_CHECKPOINT.json', {'model_id': spec['model_id'],
        'license': spec['license'], 'files': spec['files'], 'verified': True,
        'code_revision': PAYLOAD['funasr_revision']})
    return root


def worker(name, gpu, records):
    import numpy as np, torch
    from funasr import AutoModel
    torch.set_num_threads(2)
    torch.cuda.set_device(gpu)
    random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    started = time.monotonic()
    try:
        root = checkpoint(name)
        model = AutoModel(model=str(root), device=f'cuda:{gpu}', disable_update=True)
        model.model.eval()
        ids, means, meanstd, native, targetmass, rawscores = [], [], [], [], [], []
        native_labels = None
        target_classes = ['angry', 'happy', 'neutral', 'sad']
        for count, record in enumerate(records, 1):
            with torch.inference_mode():
                res = model.generate(input=record['path'], granularity='frame', extract_embedding=True)
            if isinstance(res, tuple): res = res[0]
            assert isinstance(res, list) and len(res) == 1, type(res)
            item = res[0]
            fr = np.asarray(item['feats'], dtype=np.float32)
            assert fr.ndim == 2 and fr.shape[0] > 0 and np.isfinite(fr).all()
            scores = np.asarray(item['scores'], dtype=np.float64)
            labels = [str(x).split('/')[-1].lower() for x in item['labels']]
            assert len(scores) == len(labels) and np.isfinite(scores).all() and (scores >= 0).all()
            assert np.isclose(scores.sum(), 1, atol=1e-6)
            if native_labels is None: native_labels = labels
            assert labels == native_labels and all(c in labels for c in target_classes)
            p = scores[[labels.index(c) for c in target_classes]]
            mass = float(p.sum()); assert mass > 0
            ids.append(record['Id']); means.append(fr.mean(0))
            meanstd.append(np.concatenate((fr.mean(0), fr.std(0))))
            native.append(p / mass); targetmass.append(mass); rawscores.append(scores)
            if count % 100 == 0:
                print(f'{name} GPU{gpu} {count}/{len(records)}', flush=True)
        path = OUT / f'{name}_CACHED.npz'
        np.savez_compressed(path, Id=np.asarray(ids), utterance=np.stack(means),
            meanstd=np.stack(meanstd), native=np.stack(native),
            target_mass=np.asarray(targetmass), raw_native_scores=np.stack(rawscores))
        dump(OUT / f'{name}_RESULT.json', {'status': 'PASS', 'model': name,
            'gpu': gpu, 'gpu_name': torch.cuda.get_device_name(gpu),
            'rows': len(ids), 'utterance_shape': list(np.stack(means).shape),
            'meanstd_shape': list(np.stack(meanstd).shape), 'native_labels': native_labels,
            'artifact': path.name, 'sha256': sha(path),
            'wall_seconds': time.monotonic() - started,
            'extract_count_per_row': 1, 'protected_validation_accessed': False})
        print(f'{name}=SUCCESS', flush=True)
    except Exception as e:
        dump(OUT / f'{name}_RESULT.json', {'status': 'ERROR', 'model': name,
            'gpu': gpu, 'error': str(e), 'traceback': traceback.format_exc()})
        traceback.print_exc()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', '--no-cache-dir',
        'modelscope==1.40.1', 'transformers==4.57.1', 'librosa==0.11.0', 'soundfile==0.13.1',
        'git+https://github.com/modelscope/FunASR.git@' + PAYLOAD['funasr_revision']])
    import pandas as pd, torch
    assert torch.cuda.is_available() and torch.cuda.device_count() >= 2
    raw = gzip.decompress(base64.b64decode(PAYLOAD['manifest_gzip_b64']))
    assert hashlib.sha256(raw).hexdigest() == PAYLOAD['manifest_sha256']
    manifest = OUT / 'DATA_MANIFEST.csv'; manifest.write_bytes(raw)
    dm = pd.read_csv(manifest)
    assert len(dm) == 1035 and dm.Id.is_unique
    roots = []
    for p in INPUT.rglob('train.csv'):
        if (p.parent / 'train').is_dir() and (p.parent / 'test').is_dir(): roots.append(p.parent)
    roots = sorted(set(roots)); assert len(roots) == 1, roots
    root = roots[0]; records = []
    for r in dm.sort_values('Id').itertuples(index=False):
        p = root / r.split / r.filename
        assert p.exists() and sha(p) == r.file_sha256, p
        assert r.sample_rate == 16000 and r.channels == 1
        records.append({'Id': int(r.Id), 'path': str(p)})
    dump(OUT / 'EXECUTION_PROVENANCE.json', {'mission': 'RS-DEFHS-SCORE-PUSH-001',
        'source_sha': PAYLOAD['source_sha'], 'source_template_sha256': PAYLOAD['template_sha256'],
        'config_sha256': PAYLOAD['config_sha256'], 'manifest_sha256': sha(manifest),
        'audio_hashes_verified': len(records), 'gpu_names': [torch.cuda.get_device_name(i) for i in range(2)],
        'assignments': {'emotion2vec_plus_base': 0, 'emotion2vec_plus_large': 1},
        'packages': {p: importlib.metadata.version(p) for p in ['torch', 'numpy', 'pandas', 'funasr', 'modelscope', 'transformers', 'soundfile']},
        'protected_validation_accessed': False, 'kaggle_submission_made': False})
    ctx = mp.get_context('spawn')
    workers = [ctx.Process(target=worker, args=(name, gpu, records))
               for gpu, name in enumerate(['emotion2vec_plus_base', 'emotion2vec_plus_large'])]
    for w in workers: w.start()
    for w in workers: w.join()
    results = {n: json.loads((OUT / f'{n}_RESULT.json').read_text())
        if (OUT / f'{n}_RESULT.json').exists() else {'status': 'CRASH', 'exitcode': workers[i].exitcode}
        for i, n in enumerate(['emotion2vec_plus_base', 'emotion2vec_plus_large'])}
    dump(OUT / 'EXTRACTION_RESULTS.json', results)
    dump(OUT / 'OUTPUT_INVENTORY.json', {'files': [{'name': p.name, 'bytes': p.stat().st_size,
        'sha256': sha(p)} for p in sorted(OUT.iterdir()) if p.is_file()]})
    print(json.dumps({k: v['status'] for k, v in results.items()}), flush=True)
    print('PROTECTED_VALIDATION_NOT_ACCESSED=TRUE', flush=True)
    print('KAGGLE_SUBMISSION_NOT_MADE=TRUE', flush=True)
    if not any(r['status'] == 'PASS' for r in results.values()): raise RuntimeError('Both fixed audio candidates failed; inspect exact worker tracebacks.')


if __name__ == '__main__': main()
