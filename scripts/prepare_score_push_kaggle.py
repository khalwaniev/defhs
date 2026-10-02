#!/usr/bin/env python3
"""Build a private extraction package using only explicitly allowed inputs."""
import base64, gzip, hashlib, json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001'


def main():
    config = json.loads((RUN / 'MISSION_CONFIG.json').read_text())
    template = ROOT / 'scripts/score_push_audio_extract.py'
    manifest = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv'
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha(manifest) == '1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469'
    payload = {'models': config['audio_models'], 'funasr_revision': config['funasr_revision'],
        'manifest_gzip_b64': base64.b64encode(gzip.compress(manifest.read_bytes(), mtime=0)).decode(),
        'manifest_sha256': sha(manifest), 'template_sha256': sha(template),
        'config_sha256': sha(RUN / 'MISSION_CONFIG.json'),
        'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    package = ROOT / 'kaggle/rs_score_push_001_audio'; package.mkdir(parents=True, exist_ok=True)
    source = template.read_text().replace('PAYLOAD = {}  # Replaced by the package builder with the exact small input contract.',
                                         'PAYLOAD = ' + repr(payload))
    (package / 'run.py').write_text(source)
    metadata = {'id': 'khalwaniev/defhs-rs-score-push-audio', 'title': 'DEFHS RS Score Push Audio',
        'code_file': 'run.py', 'language': 'python', 'kernel_type': 'script', 'is_private': True,
        'enable_gpu': True, 'enable_internet': True, 'machine_shape': 'NvidiaTeslaT4',
        'competition_sources': ['dataverse-detecting-emotions-from-hindi-speech'],
        'dataset_sources': [], 'kernel_sources': [], 'model_sources': []}
    (package / 'kernel-metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print('BUILT', package, 'source_sha', payload['source_sha'], 'runner_sha256', sha(package / 'run.py'))


if __name__ == '__main__': main()
