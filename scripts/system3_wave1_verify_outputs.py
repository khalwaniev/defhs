#!/usr/bin/env python3
"""Verify a completed Wave1 package before metrics or Drive preservation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from defhs_frozen_closure_utils import sha256, dump

def verify(root: Path):
    manifest = root / 'SHA256_MANIFEST.json'
    authority = json.loads(manifest.read_text())
    registered = set()
    total = 0
    for item in authority['files']:
        relative = Path(item['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        assert relative.as_posix() not in registered, relative
        registered.add(relative.as_posix())
        path = root / relative
        assert path.is_file(), relative
        assert path.stat().st_size == item['bytes'], relative
        assert sha256(path) == item['sha256'], relative
        total += item['bytes']
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
              and p.name != 'SHA256_MANIFEST.json'}
    assert actual == registered, {'unexpected': sorted(actual-registered), 'missing': sorted(registered-actual)}
    exits = json.loads((root/'JOB_EXIT_STATUS.json').read_text())
    assert exits['worker_exitcodes'] == [0, 0], exits
    assert not list(root.glob('*ERROR.json'))
    provenance = json.loads((root/'GPU_EXECUTION_PROVENANCE.json').read_text())
    assert provenance['protected_validation_read'] is False
    assert provenance['kaggle_submission_made'] is False
    assert provenance['audio_hashes_verified'] == 826
    return {'status': 'PASS', 'package_root': str(root.resolve()),
            'files': len(registered), 'bytes': total, 'manifest_sha256': sha256(manifest),
            'source_sha': provenance['source_sha'], 'protected_validation_read': False,
            'kaggle_submission_made': False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    parser.add_argument('--record', type=Path)
    args = parser.parse_args()
    result = verify(args.root)
    if args.record:
        assert args.record.resolve().is_relative_to(args.root.resolve()) is False
        dump(args.record, result)
    print(json.dumps(result, indent=2))
