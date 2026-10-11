#!/usr/bin/env python3
"""Sealed, label-blind Qwen3-14B inference; assembled into the Kaggle runner.

One configuration only. A failed feasibility check is an execution outcome,
never a scientific rejection. No labels, folds, audio features, or test rows.
"""
import base64, csv, gzip, hashlib, importlib.metadata, json, math, os
import shutil, subprocess, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path

PAYLOAD = None  # Assembly replaces this literal, without importing any labels.
OUT = Path(os.environ.get('DEFHS_SEMANTIC_OUT', '/kaggle/working/final_semantic_train826'))
STATES = ['angry', 'happy', 'neutral', 'sad', 'unclear']
BATCH = 4

def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8 << 20), b''): h.update(chunk)
    return h.hexdigest()

def save(name, data):
    p = OUT / name
    tmp = p.with_suffix(p.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(p)

def main():
    wall_start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=True)
    assert PAYLOAD and PAYLOAD['model_id'] == 'Qwen/Qwen3-14B'
    raw = gzip.decompress(base64.b64decode(PAYLOAD['records_gzip_b64']))
    assert hashlib.sha256(raw).hexdigest() == PAYLOAD['input_sha256']
    rows = json.loads(raw)
    assert len(rows) == 826 and len({r['Id'] for r in rows}) == 826
    assert all(set(r) == {'Id', 'transcript'} for r in rows)
    assert hashlib.sha256(PAYLOAD['prompt'].encode()).hexdigest() == PAYLOAD['prompt_sha256']
    unique = list(dict.fromkeys(r['transcript'] for r in rows))
    assert len(unique) == 711
    contract = hashlib.sha256(json.dumps(PAYLOAD, sort_keys=True).encode()).hexdigest()
    if (OUT / 'CONTRACT.json').exists():
        assert json.loads((OUT / 'CONTRACT.json').read_text())['sha256'] == contract
    save('CONTRACT.json', {'sha256': contract, 'input_sha256': PAYLOAD['input_sha256'],
        'model': PAYLOAD['model_id'], 'revision': PAYLOAD['revision'],
        'prompt_sha256': PAYLOAD['prompt_sha256'], 'rows': 826,
        'model_input_fields': ['transcript'], 'labels_or_test_inputs_present': False})
    os.environ.setdefault('HF_HOME', '/tmp/defhs_final_qwen14b')
    os.environ['HF_HUB_DISABLE_XET'] = '1'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--quiet',
        'transformers==4.57.1', 'accelerate==1.11.0', 'bitsandbytes==0.48.1',
        'huggingface-hub==0.36.0', 'safetensors==0.6.2'], check=True)
    import torch
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
    assert torch.cuda.is_available(), 'EXECUTION_BLOCKED: no CUDA GPU'
    assert torch.cuda.device_count() == 2, 'Use the frozen dual-T4 configuration'
    assert all('T4' in torch.cuda.get_device_name(i) for i in range(2)), 'Dual T4 required'
    torch.manual_seed(20261011)
    torch.set_num_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    hfhome = Path(os.environ['HF_HOME']); hfhome.mkdir(parents=True, exist_ok=True)
    if not list(hfhome.rglob('model-00008-of-00008.safetensors')):
        assert shutil.disk_usage(hfhome).free >= 34 * 2**30, 'Need 34 GiB free model-cache disk'
    t = time.monotonic()
    model_dir = Path(snapshot_download(PAYLOAD['model_id'], revision=PAYLOAD['revision'],
        allow_patterns=list(PAYLOAD['model_files']), max_workers=4))
    download_s = time.monotonic() - t
    checked = []
    for name, spec in PAYLOAD['model_files'].items():
        p = model_dir / name
        assert p.stat().st_size == spec['bytes'], name
        h = digest(p)
        if spec['sha256'] is not None: assert h == spec['sha256'], name
        checked.append({'name': name, 'bytes': p.stat().st_size, 'sha256': h})
    save('CHECKPOINT.json', {'model_id': PAYLOAD['model_id'], 'revision': PAYLOAD['revision'],
        'files': checked, 'license': 'Apache-2.0', 'download_seconds': download_s})
    tokenizer = AutoTokenizer.from_pretrained(model_dir, padding_side='left', trust_remote_code=False)
    if tokenizer.pad_token_id is None: tokenizer.pad_token = tokenizer.eos_token
    t = time.monotonic()
    model = AutoModelForCausalLM.from_pretrained(model_dir,
        quantization_config=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.float16),
        torch_dtype=torch.float16, device_map='balanced',
        max_memory={0: '13GiB', 1: '13GiB'}, attn_implementation='sdpa', trust_remote_code=False)
    model.eval()
    assert set(str(v) for v in model.hf_device_map.values()).issubset({'0','1','cuda:0','cuda:1'})
    load_s = time.monotonic() - t
    seq = {label: tokenizer.encode(label, add_special_tokens=False) for label in STATES}
    assert all(tokenizer.decode(ids) == label for label, ids in seq.items())
    eos = tokenizer.eos_token_id
    texts = {s: tokenizer.apply_chat_template([
        {'role': 'system', 'content': PAYLOAD['prompt']},
        {'role': 'user', 'content': 'Transcript:\n' + s}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False) for s in unique}
    lengths = {s: len(tokenizer.encode(t, add_special_tokens=False)) for s, t in texts.items()}
    assert max(lengths.values()) <= 512, 'Do not truncate or change configuration'
    def infer(batch):
        inputs = tokenizer([texts[s] for s in batch], padding='max_length', max_length=512,
            truncation=False, add_special_tokens=False, return_tensors='pt').to(model.get_input_embeddings().weight.device)
        prefix = inputs['input_ids'].shape[1]
        def trie(batch_id, tokens):
            suffix = tokens[prefix:].tolist()
            if eos in suffix: return [eos]
            allowed = set()
            for candidate in seq.values():
                if candidate[:len(suffix)] == suffix:
                    allowed.add(eos if len(candidate) == len(suffix) else candidate[len(suffix)])
            assert allowed, suffix
            return sorted(allowed)
        with torch.inference_mode():
            generated = model.generate(**inputs, do_sample=False, num_beams=1, max_new_tokens=16,
                temperature=None, top_p=None, top_k=None, eos_token_id=eos,
                pad_token_id=tokenizer.pad_token_id, prefix_allowed_tokens_fn=trie)
        result = tokenizer.batch_decode(generated[:, prefix:], skip_special_tokens=True)
        assert all(s in STATES for s in result), result
        for i in range(2): torch.cuda.synchronize(i)
        return result
    for i in range(2): torch.cuda.reset_peak_memory_stats(i)
    pilot = sorted(unique, key=lambda s: (-lengths[s], s))[:BATCH]
    t = time.monotonic(); pilot_labels = infer(pilot); warm_s = time.monotonic() - t
    t = time.monotonic(); repeat = infer(pilot); measured_s = time.monotonic() - t
    assert pilot_labels == repeat, 'Label reproducibility failed on label-blind pilot'
    gpu = [{'index': i, 'name': torch.cuda.get_device_name(i),
        'total_bytes': torch.cuda.get_device_properties(i).total_memory,
        'peak_allocated_bytes': torch.cuda.max_memory_allocated(i),
        'peak_reserved_bytes': torch.cuda.max_memory_reserved(i)} for i in range(2)]
    projected_s = warm_s + math.ceil(len(unique) / BATCH) * measured_s * 2
    deadline = datetime.fromisoformat('2026-10-12T18:30:00+00:00')
    remaining_s = (deadline - datetime.now(timezone.utc)).total_seconds()
    gates = {'gpu_memory_margin_at_least_2GiB': all(
        g['peak_reserved_bytes'] <= g['total_bytes'] - 2*2**30 for g in gpu),
        'projected_inference_at_most_2h': projected_s <= 7200,
        'deadline_reserves_6h_for_evaluation': remaining_s - projected_s >= 21600,
        'pilot_exact_repeat': pilot_labels == repeat}
    status = 'PASS' if all(gates.values()) else 'EXECUTION_INFEASIBLE'
    save('FEASIBILITY.json', {'status': status, 'gates': gates, 'gpu': gpu,
        'device_map': model.hf_device_map, 'download_seconds': download_s,
        'load_seconds': load_s, 'pilot_first_seconds': warm_s, 'pilot_repeat_seconds': measured_s,
        'forecast_with_2x_margin_seconds': projected_s, 'remaining_deadline_seconds': remaining_s,
        'batch': BATCH, 'fixed_padded_input_tokens': 512, 'max_actual_input_tokens': max(lengths.values()),
        'pilot_text_sha256': [hashlib.sha256(s.encode()).hexdigest() for s in pilot],
        'packages': {p: importlib.metadata.version(p) for p in
            ['torch','transformers','accelerate','bitsandbytes','huggingface-hub','safetensors']},
        'python': sys.version, 'cuda': torch.version.cuda, 'scientific_negative': False})
    assert status == 'PASS', 'Feasibility stop; preserve incumbent; do not switch model'
    print('FEASIBILITY=PASS; starting frozen train826 inference', flush=True)
    cache_path = OUT / 'UNIQUE_OUTPUTS.jsonl'
    cache = {}
    if cache_path.exists():
        for line in cache_path.read_text().splitlines():
            r = json.loads(line)
            assert r['contract_sha256'] == contract and r['label'] in STATES and r['transcript'] in unique
            assert r['transcript'] not in cache
            cache[r['transcript']] = r['label']
    with cache_path.open('a') as journal:
        def record(batch, labels):
            for s, label in zip(batch, labels):
                if s in cache:
                    assert cache[s] == label
                    continue
                cache[s] = label
                journal.write(json.dumps({'transcript':s,'label':label,'contract_sha256':contract}, ensure_ascii=False)+'\n')
            journal.flush(); os.fsync(journal.fileno())
        record(pilot, pilot_labels)
        pending = [s for s in unique if s not in cache]
        infer_start = time.monotonic()
        for offset in range(0, len(pending), BATCH):
            batch = pending[offset:offset+BATCH]
            record(batch, infer(batch))
            print(f'TRAIN_UNIQUE={len(cache)}/{len(unique)}', flush=True)
    assert len(cache) == len(unique)
    with (OUT/'QWEN14B_TRAIN826.csv').open('w', newline='') as f:
        w=csv.DictWriter(f, fieldnames=['Id','semantic_label']);w.writeheader()
        w.writerows({'Id':r['Id'],'semantic_label':cache[r['transcript']]} for r in rows)
    save('RESULT.json', {'status':'INFERENCE_COMPLETE_NOT_EVALUATED','rows':826,'unique':711,
        'output_sha256':digest(OUT/'QWEN14B_TRAIN826.csv'), 'wall_seconds':time.monotonic()-wall_start,
        'post_pilot_inference_seconds':time.monotonic()-infer_start,
        'gpu_allocated_hours_upper_bound':2*(time.monotonic()-wall_start)/3600,
        'protected_validation_accessed':False,'target209_inferred':False,'kaggle_submission':False})
    save('OUTPUT_INVENTORY.json', {p.name:{'bytes':p.stat().st_size,'sha256':digest(p)}
        for p in sorted(OUT.iterdir()) if p.is_file() and p.name!='OUTPUT_INVENTORY.json'})

if __name__ == '__main__':
    try: main()
    except BaseException:
        OUT.mkdir(parents=True, exist_ok=True)
        save('ERROR.json', {'status':'EXECUTION_BLOCKED_OR_FAILED','scientific_negative':False,
            'traceback':traceback.format_exc()})
        raise
