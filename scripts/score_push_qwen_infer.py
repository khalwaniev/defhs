#!/usr/bin/env python3
"""One fixed transcript-only semantic pass. No labels or fold data in this package."""
import base64, gzip, hashlib, importlib.metadata, json, os, subprocess, sys, time, traceback
from pathlib import Path

PAYLOAD = {}  # Replaced by the package builder with the exact small input contract.
OUT = Path('/kaggle/working/rs_defhs_score_push_001_semantic')


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()


def save(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + '\n')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    os.environ['HF_HOME'] = '/tmp/defhs_qwen_hf'
    os.environ['HF_HUB_DISABLE_XET'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet',
        'transformers==4.57.1', 'accelerate==1.11.0', 'bitsandbytes==0.48.1',
        'huggingface-hub==0.36.0', 'safetensors==0.6.2'], check=True)
    import torch, numpy as np, pandas as pd
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    torch.manual_seed(20261002); np.random.seed(20261002); torch.set_num_threads(2)
    assert torch.cuda.is_available()
    raw = gzip.decompress(base64.b64decode(PAYLOAD['transcripts_gzip_b64']))
    assert hashlib.sha256(raw).hexdigest() == PAYLOAD['transcripts_payload_sha256']
    records = json.loads(raw)
    assert len(records) == 1035 and len({r['Id'] for r in records}) == 1035
    assert all(set(r) == {'Id', 'transcript'} for r in records)
    prompt = PAYLOAD['prompt']
    assert hashlib.sha256(prompt.encode()).hexdigest() == PAYLOAD['prompt_sha256']
    (OUT / 'QWEN_FIXED_PROMPT.txt').write_text(prompt)
    model_dir = Path(snapshot_download(PAYLOAD['model_id'], revision=PAYLOAD['revision'],
        allow_patterns=list(PAYLOAD['model_files']), max_workers=4))
    checked = []
    for name, spec in PAYLOAD['model_files'].items():
        p = model_dir / name
        assert p.stat().st_size == spec['bytes'], name
        digest = sha(p)
        if spec.get('sha256'): assert digest == spec['sha256'], name
        checked.append({'name': name, 'bytes': p.stat().st_size, 'sha256': digest})
    save('CHECKPOINT.json', {'model_id': PAYLOAD['model_id'], 'revision': PAYLOAD['revision'],
        'license': 'Apache-2.0', 'files': checked, 'quantization': 'NF4 4bit doublequant FP16'})
    tokenizer = AutoTokenizer.from_pretrained(model_dir, padding_side='left')
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_dir,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16),
        torch_dtype=torch.float16, device_map={'': 0}, attn_implementation='sdpa')
    model.eval()
    allowed = ['angry', 'happy', 'neutral', 'sad', 'unclear']
    sequences = {label: tokenizer.encode(label, add_special_tokens=False) for label in allowed}
    assert all(tokenizer.decode(tokens) == label for label, tokens in sequences.items())
    eos = tokenizer.eos_token_id
    save('EXECUTION_PROVENANCE.json', {'source_sha': PAYLOAD['source_sha'],
        'audio_parent_lock_sha256': PAYLOAD['audio_parent_lock_sha256'],
        'prompt_sha256': PAYLOAD['prompt_sha256'], 'source_ASR_sha256': PAYLOAD['source_ASR_sha256'],
        'template_sha256': PAYLOAD['template_sha256'], 'input_payload_sha256': PAYLOAD['transcripts_payload_sha256'],
        'input_fields_to_model': ['transcript'], 'enable_thinking': False,
        'decoding': 'greedy exact label token trie then EOS', 'batch_size': 16,
        'allowed_label_tokens': sequences, 'gpu_name': torch.cuda.get_device_name(0),
        'seed': 20261002, 'model': PAYLOAD['model_id'], 'revision': PAYLOAD['revision'],
        'packages': {n: importlib.metadata.version(n) for n in
            ['torch', 'transformers', 'bitsandbytes', 'accelerate', 'huggingface-hub', 'safetensors']},
        'protected_validation_accessed': False, 'kaggle_submission_made': False})
    # Exact string duplicates share one fixed semantic output. Id stays outside chat.
    unique = list(dict.fromkeys(r['transcript'] for r in records))
    cache_path = OUT / 'UNIQUE_TRANSCRIPT_OUTPUTS.jsonl'
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            r = json.loads(line); assert r['label'] in allowed
            cache[r['transcript']] = r['label']
    pending = [text for text in unique if text not in cache]
    start = time.monotonic()
    with cache_path.open('a') as journal:
        for offset in range(0, len(pending), 16):
            batch = pending[offset:offset + 16]
            chats = [tokenizer.apply_chat_template([
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': 'Transcript:\n' + text}],
                tokenize=False, add_generation_prompt=True, enable_thinking=False) for text in batch]
            inputs = tokenizer(chats, padding=True, return_tensors='pt', add_special_tokens=False).to('cuda:0')
            prefix_len = inputs['input_ids'].shape[1]
            assert prefix_len < 4096, 'Unexpected transcript length; do not silently truncate.'
            def trie(batch_id, tokens):
                suffix = tokens[prefix_len:].tolist()
                if eos in suffix: return [eos]
                options = set()
                for candidate in sequences.values():
                    if candidate[:len(suffix)] == suffix:
                        options.add(eos if len(candidate) == len(suffix) else candidate[len(suffix)])
                assert options, suffix
                return sorted(options)
            with torch.inference_mode():
                generated = model.generate(**inputs, do_sample=False, num_beams=1, max_new_tokens=16,
                    temperature=None, top_p=None, top_k=None, eos_token_id=eos,
                    pad_token_id=tokenizer.pad_token_id, prefix_allowed_tokens_fn=trie)
            outputs = tokenizer.batch_decode(generated[:, prefix_len:], skip_special_tokens=True)
            for text, label in zip(batch, outputs):
                assert label in allowed, repr(label)
                cache[text] = label
                journal.write(json.dumps({'transcript': text, 'label': label}, ensure_ascii=False) + '\n')
            journal.flush()
            print(f'QWEN_UNIQUE_DONE={len(cache)}/{len(unique)}', flush=True)
    assert len(cache) == len(unique)
    table = pd.DataFrame({'Id': [r['Id'] for r in records],
        'semantic_label': [cache[r['transcript']] for r in records]})
    table.to_csv(OUT / 'QWEN_SEMANTIC_OUTPUTS.csv', index=False)
    save('SEMANTIC_INFERENCE_RESULT.json', {'status': 'PASS', 'rows': len(table),
        'unique_transcripts': len(unique), 'completed_unique': len(cache),
        'wall_inference_seconds': time.monotonic() - start,
        'output_sha256': sha(OUT / 'QWEN_SEMANTIC_OUTPUTS.csv'),
        'one_pass_per_exact_unique_text': True, 'prompt_search': False,
        'protected_validation_accessed': False, 'kaggle_submission_made': False})
    save('OUTPUT_INVENTORY.json', {'files': [{'name': p.name, 'bytes': p.stat().st_size,
        'sha256': sha(p)} for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'OUTPUT_INVENTORY.json']})
    print('QWEN_SEMANTIC_INFERENCE=SUCCESS', flush=True)


if __name__ == '__main__':
    try: main()
    except BaseException:
        OUT.mkdir(parents=True, exist_ok=True)
        save('ERROR.json', {'traceback': traceback.format_exc()})
        raise
