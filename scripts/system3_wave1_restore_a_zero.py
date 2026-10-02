#!/usr/bin/env python3
"""Repair A's zero-epoch outer predictions from unchanged valid pilot states.

No classifier refitting, encoder inference, epoch selection, or training.
Original Kaggle packages and predictions remain immutable.
"""
import json,subprocess
from pathlib import Path
import numpy as np,torch
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import CLASSES,dump,sha256
from system3_wave1_cpu import ROOT,RUN,WORK,inputs,idhash
from system3_wave1_collect import delta,convention

def main():
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=ROOT/'.tmp/system3_wave1_vb_seed1/rs_system3_wave1_001'
    manifest={x['path']:x for x in json.loads((raw/'SHA256_MANIFEST.json').read_text())['files']}
    folds,masks,control,x=inputs();f=folds['VB'];fs=f.fold.to_numpy();X=x['emotion2vec_base'];assert X.shape==(826,1536)
    y=np.array([list(CLASSES).index(v) for v in f.emotion]);prob={arm:np.zeros((826,4)) for arm in ['A0','A1']};audit=[];inventory=[]
    torch.set_num_threads(2)
    with threadpool_limits(limits=2):
        for outer in range(5):
            H=fs==outer;S=~H;g=(outer+1)%5;G=S&(fs==g);pilot=S&~G
            scaler=StandardScaler().fit(X[pilot]);mean=torch.tensor(scaler.mean_,dtype=torch.float32);scale=torch.tensor(scaler.scale_,dtype=torch.float32)
            z=(torch.tensor(X,dtype=torch.float32)-mean)/scale;heads={};checks=[]
            for arm in ['A0','A1']:
                meta=json.loads((raw/f'A_VB_seed20260930/{arm}_fold{outer}_RESULT.json').read_text())
                assert meta['selected_epoch']==meta['pilot']['selected_epoch']==meta['refit']['selected_epoch']==0
                assert meta['pilot']['fingerprint']['training_ID_sha256']==idhash(f.Id[pilot])
                assert meta['pilot']['fingerprint']['stopping_ID_sha256']==idhash(f.Id[G])
                assert meta['prediction_ID_sha256']==idhash(f.Id[H])
                relative=f'A_VB_seed20260930/{arm}_fold{outer}_pilot_BEST.pt';path=raw/relative
                assert path.stat().st_size==manifest[relative]['bytes'] and sha256(path)==manifest[relative]['sha256']
                state=torch.load(path,map_location='cpu',weights_only=True)
                assert state['epoch']==0 and not state['encoder_delta']
                head=state['head'];assert head['weight'].shape==(4,1536) and head['bias'].shape==(4,)
                p=torch.softmax(torch.nn.functional.linear(z,head['weight'],head['bias']),dim=1).numpy()
                ce=float(-np.log(p[G,np.asarray(y[G])].clip(1e-15)).mean())
                ce_error=abs(ce-meta['pilot']['best_stopping_CE']);assert ce_error<2e-5,(outer,arm,ce_error)
                prob[arm][H]=p[H];heads[arm]=head
                checks.append({'arm':arm,'pilot_initializer_sha256':sha256(path),'pilot_stop_CE_error':ce_error})
            assert torch.equal(heads['A0']['weight'],heads['A1']['weight']) and torch.equal(heads['A0']['bias'],heads['A1']['bias'])
            path=WORK/f'A_SHARED_INITIALIZER_VB_fold{outer}.npz';np.savez_compressed(path,weight=heads['A0']['weight'].numpy(),bias=heads['A0']['bias'].numpy(),mean=mean.numpy(),scale=scale.numpy(),initialization_Ids=f.Id[pilot].to_numpy())
            inventory.append({'name':path.name,'local_path':str(path),'sha256':sha256(path),'bytes':path.stat().st_size})
            audit.append({'fold':outer,'selected_epochs':0,'training_ID_sha256':idhash(f.Id[S]),'stopping_ID_sha256':idhash(f.Id[G]),'initialization_ID_sha256':idhash(f.Id[pilot]),'prediction_ID_sha256':idhash(f.Id[H]),'shared_initializer_artifact':inventory[-1],'checks':checks,'optimizer_steps':0})
    assert np.array_equal(prob['A0'],prob['A1'])
    P=np.load(WORK/'FIXED_PAIR_VB.npz')['prob'];blend=(2*P+prob['A1'])/3
    for name,p in [('A0_VB_SHARED_INIT_CORRECTED',prob['A0']),('A1_VB_SHARED_INIT_CORRECTED',prob['A1']),('Candidate_A_VB_SHARED_INIT_CORRECTED',blend)]:
        assert np.isfinite(p).all() and np.allclose(p.sum(1),1,atol=1e-6)
        path=WORK/(name+'.npz');np.savez_compressed(path,Id=f.Id.to_numpy(),prob=p);inventory.append({'name':path.name,'local_path':str(path),'sha256':sha256(path),'bytes':path.stat().st_size})
    ff={'VB':f};mm={'VB':masks['VB']};a0={'VB':prob['A0']};a1={'VB':prob['A1']}
    correction={'status':'COMPLETE','source_sha':source,'code_sha256':sha256(Path(__file__)),
        'reason':'Raw refit incorrectly re-estimated A scaler/head on four blocks. All selected epochs are zero, so reuse the verified pilot epoch-zero head and reconstruct its scaler on the exact three initializer blocks. Zero optimizer steps on refit; no repeated training or encoder extraction.',
        'fold_audit':audit,'matched_frozen':delta(a0,{'VB':control['VB']},ff,mm),'adapted_vs_matched_frozen':delta(a1,a0,ff,mm),
        'fixed_blend_vs_pair':delta({'VB':blend},{'VB':P},ff,mm),'pilot_refit_numeric_initializer_parity':'PASS','raw_package_preserved':True,'protected_read':False,'Kaggle_submission':False}
    path=RUN/'W1_E2V_ADAPTATION_RESULTS.json';data=json.loads(path.read_text());data['strict_same_initialization_correction']=correction
    standalone=correction['adapted_vs_matched_frozen']['VB']['aggregate_delta']>=.010
    marginal=convention(correction['fixed_blend_vs_pair'],.005)
    data['strict_corrected_provisional_useful']=bool(standalone or marginal);dump(path,data)
    path=RUN/'W1_FIXED_BLEND_RESULTS.json';data=json.loads(path.read_text());a=data['arms']['A'];a['raw_initialization_deviation_results']=a['results'];a['results']=correction['fixed_blend_vs_pair'];a['correction_source_sha']=source;a['correction_note']='Restored the same pilot/refit numeric initializer; original results preserved.';dump(path,data)
    path=RUN/'PROBABILITY_ARTIFACT_INVENTORY.json';data=json.loads(path.read_text());assert not any(a['name']==b['name'] for a in data['artifacts'] for b in inventory);data['artifacts']+=inventory;dump(path,data)
    print(json.dumps({'strict_A0':correction['matched_frozen']['VB']['macro_f1'],'strict_A1':correction['adapted_vs_matched_frozen']['VB']['macro_f1'],'strict_Candidate_A':correction['fixed_blend_vs_pair']['VB']['macro_f1'],'candidate_delta':correction['fixed_blend_vs_pair']['VB']['aggregate_delta'],'entry':data.get('unused'), 'provisional_useful':bool(standalone or marginal)}))
if __name__=='__main__':main()
