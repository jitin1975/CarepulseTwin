import argparse
from pathlib import Path
import numpy as np
import pandas as pd

FEATURES = ['heart_rate','spo2','systolic_bp','diastolic_bp','temperature','respiratory_rate']


def prepare(eicu_dir: str, out_dir: str, seq_len: int = 24, horizon_hours: int = 6):
    d, o = Path(eicu_dir), Path(out_dir)
    o.mkdir(parents=True, exist_ok=True)
    patient = pd.read_csv(d/'patient.csv', usecols=['patientunitstayid'], low_memory=False)
    vp = pd.read_csv(d/'vitalPeriodic.csv', usecols=['patientunitstayid','observationoffset','temperature','sao2','heartrate','respiration','systemicsystolic','systemicdiastolic'], low_memory=False)
    va = pd.read_csv(d/'vitalAperiodic.csv', usecols=['patientunitstayid','observationoffset','noninvasivesystolic','noninvasivediastolic'], low_memory=False)
    vp['hour']=(vp.observationoffset//60).astype(int); va['hour']=(va.observationoffset//60).astype(int)
    vp=vp.rename(columns={'sao2':'spo2','heartrate':'heart_rate','respiration':'respiratory_rate','systemicsystolic':'systolic_bp','systemicdiastolic':'diastolic_bp'})
    h=vp.groupby(['patientunitstayid','hour'],as_index=False)[['temperature','spo2','heart_rate','respiratory_rate','systolic_bp','diastolic_bp']].median()
    b=va.groupby(['patientunitstayid','hour'],as_index=False)[['noninvasivesystolic','noninvasivediastolic']].median()
    h=h.merge(b,on=['patientunitstayid','hour'],how='outer')
    h['systolic_bp']=h['systolic_bp'].combine_first(h['noninvasivesystolic'])
    h['diastolic_bp']=h['diastolic_bp'].combine_first(h['noninvasivediastolic'])
    h=h.drop(columns=['noninvasivesystolic','noninvasivediastolic'])
    h=h[h.patientunitstayid.isin(patient.patientunitstayid)]
    ranges={'heart_rate':(20,250),'spo2':(50,100),'systolic_bp':(40,300),'diastolic_bp':(20,200),'temperature':(25,45),'respiratory_rate':(2,80)}
    for c,(lo,hi) in ranges.items(): h.loc[(h[c]<lo)|(h[c]>hi),c]=np.nan
    h=h.sort_values(['patientunitstayid','hour'])
    # Forward-fill within stay; population medians are computed from the data available.
    h[FEATURES]=h.groupby('patientunitstayid')[FEATURES].ffill()
    h[FEATURES]=h[FEATURES].fillna(h[FEATURES].median())
    # Research target: any qualifying abnormal vital during the next 6 hours,
    # strictly after the current prediction time. This is not a diagnosis.
    h['abnormal']=((h.spo2<88)|(h.heart_rate>130)|(h.respiratory_rate>30)|(h.systolic_bp<90)).astype(np.int8)
    h['label']=0
    for _, idx in h.groupby('patientunitstayid').groups.items():
        vals=h.loc[idx,'abnormal'].to_numpy()
        labels=np.zeros(len(vals),dtype=np.int8)
        for j in range(len(vals)):
            labels[j]=vals[j+1:j+1+horizon_hours].max() if j+1<len(vals) else 0
        h.loc[idx,'label']=labels
    ids=h.patientunitstayid.unique(); rng=np.random.default_rng(42); rng.shuffle(ids)
    n=len(ids); trids=ids[:int(.70*n)]; vids=ids[int(.70*n):int(.85*n)]; teids=ids[int(.85*n):]
    def make(ids):
        X=[]; y=[]
        for _,g in h[h.patientunitstayid.isin(ids)].groupby('patientunitstayid'):
            g=g.sort_values('hour').reset_index(drop=True); arr=g[FEATURES].to_numpy(np.float32); lab=g.label.to_numpy(np.int64); hrs=g.hour.to_numpy()
            for end in range(seq_len-1,len(g)):
                if hrs[end]-hrs[end-seq_len+1] != seq_len-1: continue
                X.append(arr[end-seq_len+1:end+1]); y.append(lab[end])
        return np.asarray(X,np.float32),np.asarray(y,np.int64)
    Xtr,ytr=make(trids); Xv,yv=make(vids); Xt,yt=make(teids)
    mu=Xtr.reshape(-1,6).mean(0); sd=Xtr.reshape(-1,6).std(0); sd[sd<1e-6]=1
    np.savez_compressed(o/'sequences.npz',X_train=((Xtr-mu)/sd).astype(np.float32),y_train=ytr,X_val=((Xv-mu)/sd).astype(np.float32),y_val=yv,X_test=((Xt-mu)/sd).astype(np.float32),y_test=yt,mean=mu.astype(np.float32),std=sd.astype(np.float32),features=np.array(FEATURES))
    h.to_csv(o/'hourly_vitals.csv',index=False)
    print('train',Xtr.shape,'positive',int(ytr.sum()),'rate',round(float(ytr.mean()),4))
    print('val  ',Xv.shape,'positive',int(yv.sum()),'rate',round(float(yv.mean()),4))
    print('test ',Xt.shape,'positive',int(yt.sum()),'rate',round(float(yt.mean()),4))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--eicu-dir',required=True); ap.add_argument('--out',required=True); ap.add_argument('--seq-len',type=int,default=24); ap.add_argument('--horizon-hours',type=int,default=6)
    a=ap.parse_args(); prepare(a.eicu_dir,a.out,a.seq_len,a.horizon_hours)
