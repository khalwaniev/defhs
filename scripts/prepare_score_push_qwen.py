#!/usr/bin/env python3
"""Package only ASR Id/text, precommitted prompt, and pinned checkpoint authority."""
import base64, gzip, hashlib, json, subprocess
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001'


def main():
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    cfg = json.loads((RUN / 'MISSION_CONFIG.json').read_text())['qwen']
    lock = RUN / 'AUDIO_PARENT_LOCK.json'; assert lock.exists()
    assert json.loads(lock.read_text())['locked_before_semantic_inference']
    asr = ROOT / 'work/mission_inputs/asr_transcripts/ASR_TRANSCRIPTS.csv'
    assert sha(asr) == 'a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01'
    records = pd.read_csv(asr)[['Id', 'transcript']].fillna('').sort_values('Id').to_dict('records')
    assert len(records) == 1035
    raw = json.dumps(records, ensure_ascii=False, separators=(',', ':')).encode()
    prompt = RUN / 'QWEN_FIXED_PROMPT.txt'; assert sha(prompt) == cfg['prompt_sha256']
    meta = json.loads((ROOT / 'work/score_push_authority/Qwen3-8B_blobs.json').read_text())
    assert meta['sha'] == cfg['revision'] and not meta['private'] and not meta['gated']
    allowed = {'config.json', 'generation_config.json', 'tokenizer.json', 'tokenizer_config.json',
               'merges.txt', 'vocab.json', 'model.safetensors.index.json', 'LICENSE'}
    files = {r['rfilename']: {'bytes': r['size'], 'sha256': r.get('lfs', {}).get('sha256')}
        for r in meta['siblings'] if r['rfilename'] in allowed or r['rfilename'].endswith('.safetensors')}
    assert len([n for n in files if n.endswith('.safetensors')]) == 5
    template = ROOT / 'scripts/score_push_qwen_infer.py'
    payload = {'model_id': cfg['model_id'], 'revision': cfg['revision'], 'model_files': files,
        'prompt': prompt.read_text(), 'prompt_sha256': sha(prompt),
        'transcripts_gzip_b64': base64.b64encode(gzip.compress(raw, mtime=0)).decode(),
        'transcripts_payload_sha256': hashlib.sha256(raw).hexdigest(), 'source_ASR_sha256': sha(asr),
        'audio_parent_lock_sha256': sha(lock), 'template_sha256': sha(template),
        'source_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    p = ROOT / 'kaggle/rs_score_push_001_semantic'; p.mkdir(parents=True, exist_ok=True)
    (p / 'run.py').write_text(template.read_text().replace(
        'PAYLOAD = {}  # Replaced by the package builder with the exact small input contract.', 'PAYLOAD = ' + repr(payload)))
    (p / 'kernel-metadata.json').write_text(json.dumps({'id': 'khalwaniev/defhs-rs-score-push-semantic',
        'title': 'DEFHS RS Score Push Semantic', 'code_file': 'run.py', 'language': 'python',
        'kernel_type': 'script', 'is_private': True, 'enable_gpu': True, 'enable_internet': True,
        'machine_shape': 'NvidiaTeslaT4', 'competition_sources': [], 'dataset_sources': [],
        'kernel_sources': [], 'model_sources': []}, indent=2) + '\n')
    print('BUILT', p, 'source_sha', payload['source_sha'], 'runner_sha256', sha(p / 'run.py'))


if __name__ == '__main__': main()
