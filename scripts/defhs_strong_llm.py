#!/usr/bin/env python3
"""Frozen transcript-only Opus 4.6 experiment. No submission or fusion commands.

Inference reads a sealed Id/text-only payload, never labels or validation files.
Evaluation is a separate, offline operation after all 826 predictions exist.
Only Python's standard library is required.
"""
import argparse
import base64
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'runs/RS-DEFHS-STRONG-LLM-SEMANTIC-001'
CLASSES = ['angry', 'happy', 'neutral', 'sad']
STATES = CLASSES + ['unclear']
FOLDS = ROOT / 'runs/DS-DEFHS-VALIDATION-HARDENING-002/VALIDATION_VB_FOLDS.csv'
QWEN = ROOT / 'runs/RS-DEFHS-SCORE-PUSH-001/SEMANTIC_FUSION_OOF_VB.csv'
FOLDS_HASH = '87c6c0b33e5ea5c05b2bd2537d29480e4285cf816d4a921a6f1bcb3ef854139b'
QWEN_HASH = '7939bd5d7edc2e5c7978fd576b8f9dbc380d323791e322c6d71b45936925ba72'
C_SCORE = 0.8135577912484513
C_FOLDS = [0.7548722211207533, 0.812367374005305, 0.8494805998899284,
           0.8250607090820787, 0.8255294348949557]
API = 'https://api.anthropic.com/v1'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def table(path, expected=None):
    raw = path.read_bytes()
    if expected:
        require(digest(raw) == expected, 'Authority hash mismatch: ' + str(path))
    return list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))


def load_inputs():
    cfg = json.loads((RUN / 'CONFIG.json').read_text())
    prompt = (RUN / 'PROMPT.txt').read_text(encoding='utf-8')
    require(digest(prompt.encode()) == cfg['prompt_sha256'], 'Changed fixed prompt')
    packed = json.loads((RUN / 'TRAIN826_INPUTS.json').read_text())
    raw = gzip.decompress(base64.b64decode(packed['gzip_base64']))
    require(digest(raw) == cfg['input_payload_sha256'], 'Changed inference inputs')
    rows = json.loads(raw)
    require(len(rows) == 826 and len({r['Id'] for r in rows}) == 826, 'Expected 826 unique IDs')
    require(all(set(r) == {'Id', 'transcript'} and isinstance(r['transcript'], str) for r in rows),
            'Inference inputs must contain only Id and transcript')
    return cfg, prompt, rows


def request_body(text, cfg, prompt):
    return {'model': cfg['model_id'], 'max_tokens': cfg['max_tokens'],
            'thinking': {'type': 'adaptive'},
            'system': prompt,
            'messages': [{'role': 'user', 'content': json.dumps({'transcript': text}, ensure_ascii=False)}],
            'output_config': {'effort': cfg['effort'], 'format': {'type': 'json_schema',
                'schema': {'type': 'object', 'properties': {
                    'label': {'type': 'string', 'enum': CLASSES},
                    'sufficient_evidence': {'type': 'boolean'}},
                    'required': ['label', 'sufficient_evidence'], 'additionalProperties': False}}}}


def api_call(endpoint, key, payload=None):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(API + endpoint, data=data,
        headers={'x-api-key': key, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response), response.headers.get('request-id')
    except urllib.error.HTTPError as error:
        # Never print request headers or credentials. No automatic alternate model or retry.
        raise RuntimeError('ANTHROPIC_HTTP_' + str(error.code) + ': ' +
                           error.read().decode('utf-8', errors='replace')[:1000]) from None


def validate_answer(response, model):
    require(response.get('model') == model, 'Provider returned a different model')
    require(response.get('stop_reason') == 'end_turn', 'Incomplete/refused output; no rescue prompt allowed')
    text = ''.join(b['text'] for b in response.get('content', []) if b.get('type') == 'text')
    answer = json.loads(text)
    require(set(answer) == {'label', 'sufficient_evidence'}, 'Unexpected output fields')
    require(answer['label'] in CLASSES and type(answer['sufficient_evidence']) is bool, 'Invalid output')
    return answer


def infer(args):
    cfg, prompt, rows = load_inputs()
    args.output.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    unique = list(dict.fromkeys(r['transcript'] for r in rows))
    git_result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                text=True, capture_output=True, check=False)
    lock = {'model_id': cfg['model_id'], 'config_sha256': digest((RUN / 'CONFIG.json').read_bytes()),
            'prompt_sha256': cfg['prompt_sha256'], 'input_payload_sha256': cfg['input_payload_sha256'],
            'script_sha256': digest(Path(__file__).read_bytes()), 'rows': 826,
            'unique_transcripts': len(unique), 'input_fields_to_model': ['transcript'],
            'labels_in_inference_inputs': False, 'target209_inference': False,
            'source_git_commit': git_result.stdout.strip() if git_result.returncode == 0 else None,
            'python_version': sys.version, 'api_version': cfg['api_version']}
    lockpath = args.output / 'EXECUTION_LOCK.json'
    if lockpath.exists():
        require(json.loads(lockpath.read_text()) == lock, 'Cannot resume a different experiment')
    else:
        dump(lockpath, lock)
    key = os.getenv('ANTHROPIC_API_KEY')
    require(bool(key), 'MODEL_ACCESS_BLOCKED: ANTHROPIC_API_KEY is not set. Never paste keys into chat.')
    model, _ = api_call('/models/' + cfg['model_id'], key)
    require(model.get('id') == cfg['model_id'], 'Pinned model is unavailable')
    dump(args.output / 'MODEL_ACCESS.json', model)
    journal = args.output / 'RESPONSES.jsonl'
    completed = {}
    costs = 0.0
    if journal.exists():
        for line in journal.read_text().splitlines():
            item = json.loads(line)
            require(item['transcript_sha256'] not in completed, 'Duplicate journal response')
            require(item['model_id'] == cfg['model_id'], 'Wrong model in journal')
            require(item['label'] in CLASSES and type(item['sufficient_evidence']) is bool, 'Invalid journal')
            completed[item['transcript_sha256']] = item
            costs += item['estimated_usd']
    require(set(completed) <= {digest(t.encode()) for t in unique}, 'Unrecognized journal transcript')
    pending_request = args.output / 'PENDING_REQUEST.json'
    if pending_request.exists():
        pending_meta = json.loads(pending_request.read_text())
        if pending_meta['transcript_sha256'] in completed:
            pending_request.unlink()
        else:
            raise RuntimeError('UNRESOLVED_REQUEST: a previous API call lacks a valid journal entry; inspect LAST_RESPONSE.json before any rerun')
    pending = [t for t in unique if digest(t.encode()) not in completed]
    cutoff = dt.datetime.fromisoformat(cfg['execution_cutoff_utc'])
    with journal.open('a', encoding='utf-8') as handle:
        for n, text in enumerate(pending):
            now = dt.datetime.now(dt.timezone.utc)
            require(now < cutoff, 'DEADLINE_STOP: preserve two hours before the submission deadline')
            body = request_body(text, cfg, prompt)
            # Count tokens first so no billed generation starts without room in the cost budget.
            count_body = {k: v for k, v in body.items() if k != 'max_tokens'}
            count, _ = api_call('/messages/count_tokens', key, count_body)
            reserve = ((count['input_tokens'] + 1024) * cfg['usd_per_million_input'] +
                       cfg['max_tokens'] * cfg['usd_per_million_output']) / 1e6
            require(costs + reserve <= args.max_cost_usd, 'BUDGET_STOP: remaining cap cannot cover next request')
            dump(pending_request, {'transcript_sha256': digest(text.encode()),
                 'timestamp_utc': now.isoformat(), 'reserved_usd': reserve})
            response, request_id = api_call('/messages', key, body)
            # Preserve a failure response before validation; do not silently request another answer.
            dump(args.output / 'LAST_RESPONSE.json', response)
            answer = validate_answer(response, cfg['model_id'])
            usage = response['usage']
            require(not usage.get('cache_creation_input_tokens') and not usage.get('cache_read_input_tokens'),
                    'Unexpected cache billing; stop for cost accounting')
            cost = (usage['input_tokens'] * cfg['usd_per_million_input'] +
                    usage['output_tokens'] * cfg['usd_per_million_output']) / 1e6
            item = {'transcript_sha256': digest(text.encode()), **answer,
                    'model_id': response['model'], 'response_id': response['id'], 'request_id': request_id,
                    'request_sha256': digest(json.dumps(body, ensure_ascii=False, sort_keys=True).encode()),
                    'usage': usage, 'estimated_usd': cost, 'stop_reason': response['stop_reason'],
                    'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat()}
            handle.write(json.dumps(item, ensure_ascii=False) + '\n'); handle.flush(); os.fsync(handle.fileno())
            completed[item['transcript_sha256']] = item
            costs += cost
            pending_request.unlink()
            print(f"Completed {len(completed)}/{len(unique)} unique transcripts; estimated cost ${costs:.4f}", flush=True)
            if n >= 9:
                projected_seconds = (time.monotonic() - start) / (n + 1) * (len(pending) - n - 1)
                require(projected_seconds < (cutoff - dt.datetime.now(dt.timezone.utc)).total_seconds(),
                        'DEADLINE_STOP: observed throughput is too slow')
    require(len(completed) == len(unique), 'Incomplete prediction set')
    out = args.output / 'TRAIN826_PREDICTIONS.csv'
    with out.open('w', newline='', encoding='utf-8') as handle:
        writer = csv.DictWriter(handle, fieldnames=['Id', 'pred', 'semantic_state', 'transcript_sha256'])
        writer.writeheader()
        for r in rows:
            h = digest(r['transcript'].encode()); item = completed[h]
            writer.writerow({'Id': r['Id'], 'pred': item['label'],
                'semantic_state': item['label'] if item['sufficient_evidence'] else 'unclear', 'transcript_sha256': h})
    dump(args.output / 'EXECUTION_STATUS.json', {'status': 'COMPLETE_TRAIN826', **lock,
        'prediction_sha256': digest(out.read_bytes()), 'journal_sha256': digest(journal.read_bytes()),
        'estimated_api_usd': costs, 'wall_seconds_this_invocation': time.monotonic() - start,
        'usage': {k: sum(v['usage'].get(k, 0) for v in completed.values()) for k in ['input_tokens', 'output_tokens']},
        'api_model_determinism_guaranteed': False, 'prompt_search': False,
        'protected_validation_accessed': False, 'kaggle_submission_made': False})


def metrics(y, pred):
    require(len(y) == len(pred) and len(y) > 0, 'Metric alignment')
    require(set(y) <= set(CLASSES) and set(pred) <= set(STATES), 'Invalid metric labels')
    per = {}
    for c in CLASSES:
        tp = sum(a == c and b == c for a, b in zip(y, pred))
        fp = sum(a != c and b == c for a, b in zip(y, pred))
        fn = sum(a == c and b != c for a, b in zip(y, pred))
        per[c] = {'precision': tp / (tp + fp) if tp + fp else 0.,
                  'recall': tp / (tp + fn) if tp + fn else 0.,
                  'f1': 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.,
                  'support': tp + fn}
    cm = [[sum(a == c and b == k for a, b in zip(y, pred)) for k in STATES] for c in CLASSES]
    return {'rows': len(y), 'macro_f1': sum(v['f1'] for v in per.values()) / 4,
            'accuracy': sum(a == b for a, b in zip(y, pred)) / len(y), 'per_class': per,
            'confusion_rows': CLASSES, 'confusion_columns': STATES, 'confusion': cm,
            'abstentions': pred.count('unclear'),
            'neutral_to_sad': cm[2][3], 'sad_to_neutral': cm[3][2]}


def paired(y, new, old):
    return {'corrections': sum(n == t and o != t for t, n, o in zip(y, new, old)),
            'breakages': sum(n != t and o == t for t, n, o in zip(y, new, old)),
            'wrong_to_other_wrong': sum(n != t and o != t and n != o for t, n, o in zip(y, new, old)),
            'disagreements': sum(n != o for n, o in zip(new, old)),
            'old_neutral_sad_errors_corrected': sum({t, o} == {'neutral', 'sad'} and n == t for t, n, o in zip(y, new, old)),
            'new_neutral_sad_breakages': sum(o == t and {t, n} == {'neutral', 'sad'} for t, n, o in zip(y, new, old))}


def evaluate(args):
    cfg, _, inputs = load_inputs()
    status = json.loads((args.output / 'EXECUTION_STATUS.json').read_text())
    require(status['status'] == 'COMPLETE_TRAIN826', 'All inference must finish before evaluation')
    require(status['config_sha256'] == digest((RUN / 'CONFIG.json').read_bytes()), 'Wrong evaluation config')
    require(status['input_payload_sha256'] == cfg['input_payload_sha256'], 'Wrong inputs')
    require(status['journal_sha256'] == digest((args.output / 'RESPONSES.jsonl').read_bytes()), 'Changed journal')
    predictions = table(args.output / 'TRAIN826_PREDICTIONS.csv', status['prediction_sha256'])
    folds = sorted(table(FOLDS, FOLDS_HASH), key=lambda r: int(r['Id']))
    qwen = {int(r['Id']): r for r in table(QWEN, QWEN_HASH)}
    byid = {int(r['Id']): r for r in predictions}
    require(len(predictions) == len(byid) == 826 and set(byid) == {int(r['Id']) for r in folds}, 'Prediction IDs')
    texts = {r['Id']: r['transcript'] for r in inputs}
    for r in folds:
        i = int(r['Id'])
        require(byid[i]['transcript_sha256'] == digest(texts[i].encode()), 'Transcript mismatch')
        require(qwen[i]['emotion'] == r['emotion'] and qwen[i]['fold'] == r['fold'], 'Qwen alignment')
    y = [r['emotion'] for r in folds]
    pred = [byid[int(r['Id'])]['pred'] for r in folds]
    state = [byid[int(r['Id'])]['semantic_state'] for r in folds]
    qpred = [qwen[int(r['Id'])]['semantic_label'] for r in folds]
    results = {'status': 'STANDALONE_COMPLETE_FUSION_NOT_RUN', 'model_id': cfg['model_id'],
        'strong_forced_four_class': metrics(y, pred), 'strong_with_abstentions_as_errors': metrics(y, state),
        'qwen8b_with_abstentions_as_errors': metrics(y, qpred),
        'strong_forced_vs_qwen': paired(y, pred, qpred),
        'strong_abstaining_vs_qwen': paired(y, state, qpred),
        'system_c_recorded_macro_f1': C_SCORE, 'system_c_paired_comparison': None,
        'system_c_paired_status': 'BLOCKED_MISSING_AUTHORITATIVE_ROW_LEVEL_OOF', 'folds': []}
    refs = None
    if args.system_c_oof:
        require(args.system_c_sha256 and len(args.system_c_sha256) == 64, 'An independently trusted C checksum is required')
        crows = table(args.system_c_oof, args.system_c_sha256)
        require(len(crows) == 826 and len({int(r['Id']) for r in crows}) == 826, 'C rows')
        crows = {int(r['Id']): r for r in crows}
        require(set(crows) == set(byid), 'C IDs')
        for r in folds:
            c = crows[int(r['Id'])]
            require((c['emotion'], c['fold']) == (r['emotion'], r['fold']), 'C alignment')
        refs = [crows[int(r['Id'])]['pred'] for r in folds]
        require(abs(metrics(y, refs)['macro_f1'] - C_SCORE) < 1e-12, 'C score does not replay')
        results['system_c_paired_comparison'] = paired(y, pred, refs)
        results['system_c_paired_status'] = 'COMPLETE'
        results['system_c_oof_sha256'] = args.system_c_sha256
    for f in range(5):
        idx = [i for i, r in enumerate(folds) if int(r['fold']) == f]
        take = lambda x: [x[i] for i in idx]
        row = {'fold': f, 'strong_forced': metrics(take(y), take(pred)),
               'qwen_abstaining': metrics(take(y), take(qpred)),
               'strong_vs_qwen': paired(take(y), take(pred), take(qpred)),
               'system_c_recorded_macro_f1': C_FOLDS[f]}
        if refs:
            require(abs(metrics(take(y), take(refs))['macro_f1'] - C_FOLDS[f]) < 1e-12, 'C fold replay')
            row['strong_vs_system_c'] = paired(take(y), take(pred), take(refs))
        results['folds'].append(row)
    dump(args.output / 'COMPARISON.json', results)
    print(json.dumps({'strong_forced_macro_f1': results['strong_forced_four_class']['macro_f1'],
                      'system_c_paired_status': results['system_c_paired_status']}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['infer', 'evaluate', 'preflight'])
    parser.add_argument('--output', type=Path, default=ROOT / 'work/strong_llm_semantic_001')
    parser.add_argument('--max-cost-usd', type=float, default=10.)
    parser.add_argument('--system-c-oof', type=Path)
    parser.add_argument('--system-c-sha256')
    args = parser.parse_args()
    if args.command == 'preflight':
        cfg, _, rows = load_inputs()
        print(json.dumps({'input_rows': len(rows), 'model_id': cfg['model_id'],
            'api_key_present': bool(os.getenv('ANTHROPIC_API_KEY')),
            'model_access_tested': False, 'labels_in_inference_payload': False,
            'unique_transcripts': len({r['transcript'] for r in rows})}, indent=2))
        return
    try:
        infer(args) if args.command == 'infer' else evaluate(args)
    except Exception as error:
        args.output.mkdir(parents=True, exist_ok=True)
        dump(args.output / 'EXECUTION_FAILURE.json', {'command': args.command,
            'status': 'BLOCKED_OR_FAILED_NOT_A_SCIENTIFIC_NEGATIVE', 'error': str(error),
            'timestamp_utc': dt.datetime.now(dt.timezone.utc).isoformat()})
        print(str(error), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
