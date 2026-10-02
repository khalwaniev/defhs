#!/usr/bin/env python3
"""Conditional dependency uncertainty, without training or choosing a recipe."""
import json,numpy as np
from pathlib import Path
from run_score_push_cpu import contract
from defhs_frozen_closure_utils import dump,labels,robust
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'runs/RS-DEFHS-SYSTEM3-WAVE1-001';WORK=ROOT/'work/system3_wave1'

def main():
    authority=json.loads((RUN/'W1_SECONDARY_CONFIRMATION.json').read_text())
    assert authority['uncertainty_plan']['contrasts']==24
    for view in ['VB','VA']:assert (RUN/f'W1_CONFIRMATION_{view}_seed20260917.json').is_file()
    folds,ev,masks,_=contract();contrasts={};predictions={}
    for name in ['B1_seed20260930','B1_seed20260917','B1_seed_mean','Candidate_B_seed20260930','Candidate_B_seed20260917','Candidate_B_seed_mean']:
        predictions[name]={};ref={}
        for view in ['VB','VA']:
            if name.endswith('seed_mean'):
                filename=('B1_SEED_MEAN' if name.startswith('B1') else 'Candidate_B_SEED_MEAN')+'_'+view+'.npz'
            else:
                stem,seed=name.rsplit('_seed',1);filename=stem+'_'+view+'_seed'+seed+'.npz'
            z=np.load(WORK/filename);assert np.array_equal(z['Id'],folds[view].Id);predictions[name][view]=z['prob'].argmax(1)
            ref[view]=np.load(WORK/('B0_'+view+'_seed20260930.npz' if name.startswith('B1') else 'FIXED_PAIR_'+view+'.npz'))['prob'].argmax(1)
        for view,stratum in [('VB','all'),('VB','CLEAN'),('VA','all'),('VA','nonretrieval')]:
            contrasts[name+':'+view+':'+stratum]=ev.contrast(labels(folds[view].emotion),predictions[name][view],ref[view],masks[view][stratum])
    intervals=ev.intervals(contrasts);judgments={}
    for name,p in predictions.items():
        base=np.load(WORK/('B0_VB_seed20260930.npz' if name.startswith('B1') else 'FIXED_PAIR_VB.npz'))['prob'].argmax(1)
        main=robust(labels(folds['VB'].emotion),p['VB'],base,folds['VB'].fold.to_numpy(),intervals[name+':VB:all'])
        strict=main['pass'] and intervals[name+':VB:CLEAN']['point']>0 and intervals[name+':VA:nonretrieval']['upper']>=0
        judgments[name]={'old_conservative_gate_pass':bool(strict),'VB_robustness':main,
            'reference':'B0 seed1 (seed2/mean are stability contrasts, not separately matched controls)' if name.startswith('B1') else 'fixed 50/50 P'}
    dump(RUN/'W1_ADAPTATION_UNCERTAINTY.json',{'status':'COMPLETE','plan':authority['uncertainty_plan'],
        'intervals':intervals,'judgments':judgments,'independence_limit':'Conditional on reused ordinary-development OOF; VA/CLEAN are related views, not independent replications. No fitted component or promotion rule is changed by these intervals.'})
    print(json.dumps({k:v['old_conservative_gate_pass'] for k,v in judgments.items()}))
if __name__=='__main__':main()
