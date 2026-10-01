#!/usr/bin/env python3
"""Fit locked logistic finalist on cached embeddings; archive inference, never submit."""
from __future__ import annotations
import json,time
import joblib,numpy as np,pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from threadpoolctl import threadpool_limits
from defhs_frozen_closure_utils import *
from run_rs_defhs_frozen_closure import RUN,DS,V3,OUT

def main():
    t=time.monotonic();membership=json.loads((RUN/'FROZEN_MEMBERSHIP_CLOSURE.json').read_text())
    assert membership['selected_members']==['emotion2vec_base_L2_LOGREG']
    assert json.loads((RUN/'STAGE8_OFFSET_RESULTS.json').read_text())['decision']=='KEEP_ARGMAX'
    f=pd.read_csv(DS/'VALIDATION_VB_FOLDS.csv').sort_values('Id');dm=pd.read_csv(DS/'DATA_MANIFEST.csv')
    train=f.Id.to_numpy();test=np.sort(dm.loc[dm.split=='test','Id'].to_numpy())
    z=np.load(V3/'emotion2vec_base_meanstd.npz');ix={int(v):i for i,v in enumerate(z['Id'])};X=z['X']
    assert len(set(z['Id']))==1035 and len(train)==826 and len(test)==209
    with threadpool_limits(limits=2):
        m=make_pipeline(StandardScaler(),LogisticRegression(C=1,max_iter=5000,random_state=20261001))
        m.fit(X[[ix[int(i)] for i in train]],f.emotion.to_numpy());p=m.predict_proba(X[[ix[int(i)] for i in test]])
    assert np.array_equal(m.classes_,CLASSES) and np.isfinite(p).all()
    raw=CLASSES[p.argmax(1)];final=raw.copy();covered=np.zeros(209,bool)
    ret=pd.read_csv(DS/'RETRIEVAL_MAP_FINAL.csv');assert len(ret)==78 and not ret.conflict.any()
    labels_by_id=f.set_index('Id').emotion.to_dict();positions={int(v):i for i,v in enumerate(test)}
    for r in ret.itertuples(index=False):
        # The existing map already owns the duplicate graph. Inspect only its
        # recorded matched IDs; never infer another neighbor or confidence gate.
        matched=[int(v) for v in str(r.matched_train_Ids).replace(';',',').split(',')]
        assert matched and all(labels_by_id[i]==r.consensus_emotion for i in matched)
        i=positions[int(r.test_Id)];final[i]=r.consensus_emotion;covered[i]=True
    assert int(covered.sum())==78
    out=pd.DataFrame({'Id':test,'ser_pred':raw,'final_pred':final,'certified_retrieval_covered':covered})
    for j,c in enumerate(P_COLS):out[c]=p[:,j]
    out.to_csv(OUT/'LOCKED_FINALIST_TEST_INFERENCE.csv',index=False)
    joblib.dump(m,OUT/'LOCKED_FINALIST_ALL826_LOGISTIC.joblib')
    dump(RUN/'FINAL_SYSTEM_LOCK.json',{'mission_id':'RS-DEFHS-SYSTEM-IMPLEMENTATION-001','model':'iic/emotion2vec_base@v2.0.4 ModelScope','representation':'cached frozen final frames mean+std, 1536 dimensions',
        'head':'StandardScaler + multinomial L2 logistic C1 max_iter5000','encoder_cache_sha256':sha256(V3/'emotion2vec_base_meanstd.npz'),
        'decision':'argmax, angry/happy/neutral/sad order','SER_members':['emotion2vec_base_L2_LOGREG'],'weights':[1.0],'offsets':[0.,0.,0.,0.],
        'retrieval':'existing fixed certified unanimous-label hard override','retrieval_map_sha256':sha256(DS/'RETRIEVAL_MAP_FINAL.csv'),'test_rows':209,'certified_retrieval_test_rows':78,
        'serialized_model_sha256':sha256(OUT/'LOCKED_FINALIST_ALL826_LOGISTIC.joblib'),'test_inference_sha256':sha256(OUT/'LOCKED_FINALIST_TEST_INFERENCE.csv'),
        'training_rows':826,'training_seed_note':'20261001 is inherited logistic RNG only; no protected allocation was read or scored',
        'protected_validation_queried':False,'kaggle_submission_made':False,'wall_seconds':time.monotonic()-t,'accelerator_hours':0})
    print('LOCKED_FINALIST_ALL826_AND_209_INFERENCE=SUCCESS',flush=True)

if __name__=='__main__':main()
