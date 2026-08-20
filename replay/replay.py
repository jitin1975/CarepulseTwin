import argparse, asyncio
from pathlib import Path
import pandas as pd, httpx
F={'heartrate':'heart_rate','sao2':'spo2','systemicsystolic':'systolic_bp','systemicdiastolic':'diastolic_bp','temperature':'temperature','respiration':'respiratory_rate'}
async def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--eicu-dir',required=True); ap.add_argument('--patient-id',required=True,type=int); ap.add_argument('--api',default='http://localhost:8000'); ap.add_argument('--speed',type=float,default=120); ap.add_argument('--limit',type=int,default=0); a=ap.parse_args(); d=Path(a.eicu_dir)
    vp=pd.read_csv(d/'vitalPeriodic.csv',usecols=['patientunitstayid','observationoffset']+list(F),low_memory=False); va=pd.read_csv(d/'vitalAperiodic.csv',usecols=['patientunitstayid','observationoffset','noninvasivesystolic','noninvasivediastolic'],low_memory=False)
    vp=vp[vp.patientunitstayid==a.patient_id].copy(); va=va[va.patientunitstayid==a.patient_id].copy()
    if vp.empty: raise SystemExit('Patient not found in vitalPeriodic.csv')
    vp['hour']=(vp.observationoffset//60).astype(int); va['hour']=(va.observationoffset//60).astype(int)
    h=vp.groupby(['patientunitstayid','hour'],as_index=False)[['observationoffset','temperature','sao2','heartrate','respiration','systemicsystolic','systemicdiastolic']].median()
    b=va.groupby(['patientunitstayid','hour'],as_index=False)[['noninvasivesystolic','noninvasivediastolic']].median()
    h=h.merge(b,on=['patientunitstayid','hour'],how='left'); h['systemicsystolic']=h.systemicsystolic.combine_first(h.noninvasivesystolic); h['systemicdiastolic']=h.systemicdiastolic.combine_first(h.noninvasivediastolic); h=h.drop(columns=['noninvasivesystolic','noninvasivediastolic']).sort_values('hour').ffill().dropna()
    if a.limit:h=h.head(a.limit)
    prev=None
    async with httpx.AsyncClient(timeout=20) as c:
        for _,r in h.iterrows():
            if prev is not None: await asyncio.sleep(max(0,float(r.observationoffset-prev))*60/a.speed)
            prev=r.observationoffset; ts=(pd.Timestamp('2000-01-01',tz='UTC')+pd.Timedelta(minutes=float(r.observationoffset))).isoformat()
            payload={'patient_id':str(a.patient_id),'ts':ts,'heart_rate':float(r.heartrate),'spo2':float(r.sao2),'systolic_bp':float(r.systemicsystolic),'diastolic_bp':float(r.systemicdiastolic),'temperature':float(r.temperature),'respiratory_rate':float(r.respiration)}
            res=await c.post(a.api+'/api/v1/ingest',json=payload); res.raise_for_status(); print(res.json())
if __name__=='__main__': asyncio.run(main())
