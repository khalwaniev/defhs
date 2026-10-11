#!/usr/bin/env python3
"""SS-authorized one-shot Qwen3-ASR target209 -> FROZEN Qwen3-14B semantic inference.

Build Kaggle package from authenticated prior train826 Qwen3-14B runner,
NOT a model/prompt/quantization change. Complete input and journal audit.
No target emotion labels, model fitting, protected validation, or submissions.
"""
import argparse,ast,base64,copy,csv,gzip,hashlib,io,json,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PARENT="69ebbe3ca3c65f82e546fdf1d42e90fa885c8634"
ORIGINAL="kaggle/rs_final_semantic_train826_001/run.py"
ORIGINAL_BLOB="cd0b35bc68c13aca928a2ca8591b7be32ff2db19"
DATA="runs/DS-DEFHS-VALIDATION-HARDENING-002/DATA_MANIFEST.csv"
DATA_SHA="1e5552d42aec94efae197e7dac95de41cfc96e40336f3e513b9a87e3ccc72469"
ASR_REV="b188e100bd85038c06d2812d24a39776eba774ca"
ASR_EXPECTED_SHA="4c32a0431bff86e8e9c5153acd7225138f5790a63ff06fa001267a42ad583771"
QWEN_REV="40c069824f4251a91eefaf281ebe4c544efd3e18"
PROMPT_SHA="d34712a764dabcd5616e826e8597cbdfba18a8fbca37b16195e2e22fed77324f"
KERNEL="khalwaniev/rs-defhs-system-e-qwen14-target209-001"
OUTDIR=ROOT/"kaggle/rs_system_e_qwen14_target209_001"
NAMES=["QWEN3_ASR_TARGET209.csv","QWEN3_ASR_TARGET209_PROGRESS.jsonl",
       "ASR_TARGET209_RESULT.json","OUTPUT_INVENTORY.json"]
def sha(data):return hashlib.sha256(data).hexdigest()
def digest(p):return sha(Path(p).read_bytes())
def gitblob(b):return hashlib.sha1(("blob "+str(len(b))+"\0").encode()+b).hexdigest()
def replace1(s,before,after):
    count=s.count(before)
    assert count==1,(before,count)
    return s.replace(before,after)
def read_asr(root):
    root=Path(root)
    for n in NAMES:
        files=list(root.rglob(n))
        assert len(files)==1,("exactly one required output",n,[str(f) for f in files])
    locations={n:next(root.rglob(n)) for n in NAMES}
    assert len({p.parent for p in locations.values()})==1,"ASR outputs must share one completed-run directory"
    status=json.loads(locations["ASR_TARGET209_RESULT.json"].read_text())
    inventory=json.loads(locations["OUTPUT_INVENTORY.json"].read_text())
    assert status["status"]=="PASS" and inventory["status"]=="PASS"
    assert status["rows"]==status["unique_Ids"]==status["source_audio_verified"]==209
    assert status["model_id"]=="Qwen/Qwen3-ASR-1.7B"
    assert status["model_revision"]==inventory["revision"]==ASR_REV
    assert status["qwen_asr_version"]=="0.0.6"
    assert status["language_requested"]=="Hindi"
    assert status["test_audio_access"] is True
    assert status["protected_access"] is False
    assert status["kaggle_submitted"] is False
    assert inventory["model_id"]=="Qwen/Qwen3-ASR-1.7B"
    assert status["output_sha256"]==digest(locations["QWEN3_ASR_TARGET209.csv"])==ASR_EXPECTED_SHA, "Kaggle output CSV SHA differs from log"
    listed={s["name"]:s for s in inventory["files"]}
    assert set(listed)==set(NAMES)-{"OUTPUT_INVENTORY.json"}
    for n,entry in listed.items():
        b=locations[n].read_bytes()
        assert len(b)==entry["bytes"] and sha(b)==entry["sha256"],n
    csv_bytes=locations["QWEN3_ASR_TARGET209.csv"].read_bytes()
    rows=list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
    assert len(rows)==209 and len({int(r["Id"]) for r in rows})==209
    assert set(rows[0])=={"Id","filename","file_sha256","language","transcript"}
    journals=[json.loads(l) for l in locations["QWEN3_ASR_TARGET209_PROGRESS.jsonl"].read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(journals)==209 and len({int(r["Id"]) for r in journals})==209
    journal={int(r["Id"]):r for r in journals}
    canonical=(ROOT/DATA).read_bytes()
    assert sha(canonical)==DATA_SHA
    manifest=list(csv.DictReader(io.StringIO(canonical.decode("utf-8"))))
    trainids={int(r["Id"]) for r in manifest if r["split"]=="train"}
    test={int(r["Id"]):r for r in manifest if r["split"]=="test"}
    assert len(trainids)==826 and len(test)==209 and not trainids.intersection(test)
    assert set(journal)==set(test)=={int(r["Id"]) for r in rows}
    assert status["manifest_sha256"]=="daf7bb1b869af2f872b0ed8f3f51f5386071256f2abcd17e19b2bdfd1be5edec"
    assert status["target_ids_sha256"]=="d71971079edf16597973364358b94b3d0e69556bffe25e3db137a86b643365f2"
    rows=sorted(rows,key=lambda r:int(r["Id"]))
    for row in rows:
        k=int(row["Id"]);official=test[k];p=journal[k]
        assert official["emotion"]==""
        assert row["filename"]==p["filename"]==official["filename"]
        assert row["file_sha256"]==p["file_sha256"]==official["file_sha256"]
        assert row["transcript"]==p["transcript"] and row["transcript"].strip()
        assert row["language"]=="Hindi" and p["detected_language"]=="Hindi"
        assert p["checkpoint_revision"]==ASR_REV and p["requested_language"]=="Hindi"
        assert not any(ch in row["transcript"] for ch in "\0\r\n")
    return rows, status, locations

def build(asr_dir,out):
    rows,status,paths=read_asr(asr_dir)
    records=[{"Id":int(r["Id"]),"transcript":r["transcript"]} for r in rows]
    assert len(records)==209
    count=len(set(r["transcript"] for r in records))
    assert 1<=count<=209
    minimal=json.dumps(records,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    encoded=base64.b64encode(gzip.compress(minimal,mtime=0)).decode("ascii")
    raw=subprocess.run(["git","show",f"{PARENT}:{ORIGINAL}"],
                       cwd=ROOT,check=True,capture_output=True).stdout
    assert gitblob(raw)==ORIGINAL_BLOB
    frozen=raw.decode("utf-8")
    lines=frozen.splitlines(keepends=True)
    indices=[i for i,line in enumerate(lines) if line.startswith("PAYLOAD = ")]
    assert len(indices)==1
    i=indices[0]
    old=ast.literal_eval(ast.parse(lines[i]).body[0].value)
    assert old["model_id"]=="Qwen/Qwen3-14B" and old["revision"]==QWEN_REV
    assert sha(old["prompt"].encode())==old["prompt_sha256"]==PROMPT_SHA
    assert old["source_ASR_sha256"]=="a111071c53edd14a6202d9ac7b12360648c9f12e8650fee0aabf2dda0df12d01"
    assert len(old["model_files"])>=15
    new=copy.deepcopy(old)
    new["records_gzip_b64"]=encoded
    new["input_sha256"]=sha(minimal)
    new["source_ASR_sha256"]=ASR_EXPECTED_SHA
    new["qwenasr_revision"]=ASR_REV
    assert old["prompt"]==new["prompt"] and old["model_files"]==new["model_files"]
    lines[i]="PAYLOAD = "+repr(new)+"\n"
    code="".join(lines)
    # Changes confined to cardinality, input-field provenance and output locations.
    changes=[
        ("assert len(rows) == 826 and len({r['Id'] for r in rows}) == 826",
         "assert len(rows) == 209 and len({r['Id'] for r in rows}) == 209"),
        ("assert len(unique) == 711",f"assert len(unique) == {count}"),
        ("'rows': 826,","'rows': 209,"),
        ("'rows':826, 'unique':711",f"'rows':209, 'unique':{count}"),
        ("'labels_or_test_inputs_present': False","'labels_or_test_inputs_present': True"),
        ("'target209_inferred':False","'target209_inferred':True"),
        ("'QWEN14B_TRAIN826.csv'","'QWEN14B_TARGET209.csv'"),
        ("'/kaggle/working/final_semantic_train826'","'/kaggle/working/final_semantic_qwenasr_target209'"),
        ("'FEASIBILITY=PASS; starting frozen train826 inference'","'FEASIBILITY=PASS; starting frozen TARGET209 inference'"),
        ("'TRAIN_UNIQUE=","'TARGET_UNIQUE="),
    ]
    # The original reference file has unique 711. Replace dynamically if needed only as exact frozen code.
    for before,after in changes:
        n=code.count(before)
        if before=="'rows': 826,":
            assert n==1,(before,n)
        else:
            assert n==1,(before,n)
        code=code.replace(before,after)
    # Keep the frozen model/inference code identical outside the declared swaps.
    expected=frozen
    for before,after in changes:expected=replace1(expected,before,after)
    a=expected.splitlines(keepends=True);b=code.splitlines(keepends=True)
    assert len(a)==len(b) and all(a[j]==b[j] for j in range(len(a)) if j!=i)
    assert ast.parse(code)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    run=out/"run.py";run.write_text(code,encoding="utf-8")
    meta={"id":KERNEL,"title":"rs-defhs-system-e-qwen14-target209-001",
          "code_file":"run.py","language":"python","kernel_type":"script",
          "is_private":True,"enable_gpu":True,"enable_internet":True,
          "dataset_sources":[],"competition_sources":[],"kernel_sources":[],
          "machine_shape":"NvidiaTeslaT4"}
    (out/"kernel-metadata.json").write_text(json.dumps(meta,indent=2)+"\n")
    verification={
        "status":"SYSTEM_E_QWEN14_TARGET209_STATIC_PASS_GPU_NOT_EXECUTED",
        "mission":"SS-DEFHS-SYSTEM-E-EXPLORATORY-DEPLOYMENT-001",
        "original_frozen_runner_commit":PARENT,
        "original_frozen_runner_blob":ORIGINAL_BLOB,
        "asr_output_sha256":ASR_EXPECTED_SHA,
        "asr_model_revision":ASR_REV,
        "qwen14_model_revision":QWEN_REV,
        "prompt_sha256":PROMPT_SHA,
        "input_sha256":sha(minimal),"rows":209,"unique_transcripts":count,
        "no_emotion_labels_or_folds":True,
        "no_train_rows":True,"no_submission":True,
        "scientific_gate_Q960_passed":False,
        "frozen_inference_identical_outside_input_and_scope":True,
        "run_sha256":digest(run),
        "metadata_sha256":digest(out/"kernel-metadata.json")
    }
    (out/"PACKAGE_VERIFICATION.json").write_text(json.dumps(verification,indent=2)+"\n")
    (out/"README.md").write_text(
        "# SS-authorized System E exploratory TARGET209 semantic inference\n\n"
        "The frozen Qwen3-14B classifier runs on 209 verified Qwen3-ASR test transcripts. "
        "No emotion labels, train rows, folds or protected validation. "
        "Unchanged Qwen3-14B checkpoint, prompt, decoding, quantization and dual-T4 setup. "
        "No scientific promotion or Kaggle competition submission.\n"
        "Expected outputs in /kaggle/working/final_semantic_qwenasr_target209.\n"
    )
    print(json.dumps(verification,indent=2))
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--asr-dir",type=Path,default=ROOT/"work/system_e_target209_asr_return")
    p.add_argument("--out",type=Path,default=OUTDIR)
    v=p.parse_args()
    build(v.asr_dir,v.out)
if __name__=="__main__":main()
