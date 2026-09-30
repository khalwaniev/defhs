from pathlib import Path
import hashlib, json, math, warnings
import numpy as np, pandas as pd
from scipy.io import wavfile
from scipy.stats import entropy
import librosa
from joblib import Parallel, delayed

ROOT=Path('/mnt/data/defhs_work/SRCASW-BhavVaani')
OUT=Path('/mnt/data/defhs_ds002')
OUT.mkdir(exist_ok=True)
train=pd.read_csv(ROOT/'train.csv')
test=pd.read_csv(ROOT/'test.csv')

def _stats(a,prefix):
    a=np.asarray(a,float)
    if a.ndim==1:a=a[None,:]
    out={}
    for fn,fun in [('mean',np.nanmean),('std',np.nanstd),('p10',lambda x,axis:np.nanpercentile(x,10,axis=axis)),('p50',lambda x,axis:np.nanpercentile(x,50,axis=axis)),('p90',lambda x,axis:np.nanpercentile(x,90,axis=axis))]:
        v=fun(a,axis=1)
        for i,x in enumerate(np.ravel(v)):
            out[f'{prefix}{i:02d}_{fn}']=float(x)
    return out

def one(split,row):
    path=ROOT/split/row.filename
    raw=path.read_bytes()
    sr,x=wavfile.read(path)
    ch=1 if x.ndim==1 else x.shape[1]
    if x.ndim>1:x=x.mean(axis=1)
    orig_dtype=str(x.dtype)
    xi=np.asarray(x)
    if np.issubdtype(xi.dtype,np.integer):
        info=np.iinfo(xi.dtype); scale=max(abs(info.min),abs(info.max))
        y=xi.astype(np.float32)/scale
    else:
        y=xi.astype(np.float32); scale=1.0
    y=np.nan_to_num(y)
    n=len(y); dur=n/sr
    peak=float(np.max(np.abs(y))) if n else 0.0
    rms=float(np.sqrt(np.mean(y*y))) if n else 0.0
    dc=float(np.mean(y)) if n else 0.0
    crest=float(peak/(rms+1e-12))
    clip=float(np.mean(np.abs(y)>=0.999))
    fl=512; hop=160
    rmsf=librosa.feature.rms(y=y,frame_length=fl,hop_length=hop,center=True)[0]
    zcr=librosa.feature.zero_crossing_rate(y,frame_length=fl,hop_length=hop,center=True)[0]
    cent=librosa.feature.spectral_centroid(y=y,sr=sr,n_fft=512,hop_length=hop)[0]
    bw=librosa.feature.spectral_bandwidth(y=y,sr=sr,n_fft=512,hop_length=hop)[0]
    roll=librosa.feature.spectral_rolloff(y=y,sr=sr,n_fft=512,hop_length=hop,roll_percent=.85)[0]
    flat=librosa.feature.spectral_flatness(y=y,n_fft=512,hop_length=hop)[0]
    onset=librosa.onset.onset_strength(y=y,sr=sr,hop_length=hop)
    mfcc=librosa.feature.mfcc(y=y,sr=sr,n_mfcc=20,n_fft=512,hop_length=hop)
    dm=librosa.feature.delta(mfcc)
    mel=librosa.feature.melspectrogram(y=y,sr=sr,n_mels=32,n_fft=512,hop_length=hop,power=2.0)
    logmel=librosa.power_to_db(mel+1e-10,ref=np.max)
    maxr=float(np.max(rmsf)) if len(rmsf) else 0.0
    sil_thr=max(1e-6,maxr*0.03)
    silent=rmsf<sil_thr
    silence_frac=float(np.mean(silent)) if len(silent) else 0.0
    lead=0
    for v in silent:
        if v:lead+=1
        else:break
    trail=0
    for v in silent[::-1]:
        if v:trail+=1
        else:break
    runs=[]; c=0
    for v in silent:
        if v:c+=1
        elif c:
            runs.append(c);c=0
    if c:runs.append(c)
    pause_runs=[r for r in runs if r>=3]
    try:
        f0=librosa.yin(y,fmin=60,fmax=400,sr=sr,frame_length=1024,hop_length=hop)
        finite=f0[np.isfinite(f0)]
        if len(finite):
            f0_med=float(np.median(finite)); f0_mean=float(np.mean(finite)); f0_std=float(np.std(finite)); f0_p10=float(np.percentile(finite,10)); f0_p90=float(np.percentile(finite,90))
        else: f0_med=f0_mean=f0_std=f0_p10=f0_p90=np.nan
    except Exception:
        f0_med=f0_mean=f0_std=f0_p10=f0_p90=np.nan
    rec={
        'split':split,'Id':int(row.Id),'filename':row.filename,'emotion':getattr(row,'emotion',None),
        'sample_rate':int(sr),'channels':int(ch),'dtype':orig_dtype,'sample_width_bits':int(np.dtype(xi.dtype).itemsize*8),
        'samples':int(n),'duration_seconds':float(dur),'file_bytes':len(raw),
        'file_sha256':hashlib.sha256(raw).hexdigest(),'pcm_sha256':hashlib.sha256(xi.tobytes()).hexdigest(),
        'amplitude_peak_fullscale':peak,'rms_fullscale':rms,'dc_offset_fullscale':dc,'crest_factor':crest,'clip_fraction':clip,
        'silence_fraction':silence_frac,'leading_silence_seconds':lead*hop/sr,'trailing_silence_seconds':trail*hop/sr,
        'pause_count':len(pause_runs),'pause_fraction_frames':float(sum(pause_runs)/max(1,len(silent))),
        'zcr_mean':float(np.mean(zcr)),'zcr_std':float(np.std(zcr)),
        'spectral_centroid_mean':float(np.mean(cent)),'spectral_centroid_std':float(np.std(cent)),
        'spectral_bandwidth_mean':float(np.mean(bw)),'spectral_bandwidth_std':float(np.std(bw)),
        'spectral_rolloff85_mean':float(np.mean(roll)),'spectral_rolloff85_std':float(np.std(roll)),
        'spectral_flatness_mean':float(np.mean(flat)),'spectral_flatness_std':float(np.std(flat)),
        'rms_frame_mean':float(np.mean(rmsf)),'rms_frame_std':float(np.std(rmsf)),
        'onset_strength_mean':float(np.mean(onset)) if len(onset) else 0.0,'onset_strength_std':float(np.std(onset)) if len(onset) else 0.0,
        'f0_yin_mean':f0_mean,'f0_yin_median':f0_med,'f0_yin_std':f0_std,'f0_yin_p10':f0_p10,'f0_yin_p90':f0_p90,
    }
    rec.update(_stats(mfcc,'mfcc'))
    rec.update(_stats(dm,'dmfcc'))
    rec.update(_stats(logmel,'logmel'))
    return rec

rows=[]
for split,df in [('train',train),('test',test)]:
    rows.extend(Parallel(n_jobs=4,verbose=5)(delayed(one)(split,r) for r in df.itertuples(index=False)))
features=pd.DataFrame(rows).sort_values('Id').reset_index(drop=True)
features.to_csv(OUT/'ACOUSTIC_FEATURES_FULL.csv',index=False)
basic=['duration_seconds','amplitude_peak_fullscale','rms_fullscale','dc_offset_fullscale','crest_factor','clip_fraction','silence_fraction','leading_silence_seconds','trailing_silence_seconds','pause_count','pause_fraction_frames','zcr_mean','spectral_centroid_mean','spectral_bandwidth_mean','spectral_rolloff85_mean','spectral_flatness_mean','onset_strength_mean','f0_yin_median','f0_yin_std']
recs=[]
for col in basic:
    for split,g in features.groupby('split'):
        v=pd.to_numeric(g[col],errors='coerce').dropna()
        recs.append({'feature':col,'group':split,'n':len(v),'mean':v.mean(),'std':v.std(),'median':v.median(),'p10':v.quantile(.1),'p90':v.quantile(.9)})
    for emo,g in features[features.split=='train'].groupby('emotion'):
        v=pd.to_numeric(g[col],errors='coerce').dropna()
        recs.append({'feature':col,'group':'train:'+str(emo),'n':len(v),'mean':v.mean(),'std':v.std(),'median':v.median(),'p10':v.quantile(.1),'p90':v.quantile(.9)})
pd.DataFrame(recs).to_csv(OUT/'ACOUSTIC_FEATURE_SUMMARY.csv',index=False)
print('wrote',features.shape,OUT)
