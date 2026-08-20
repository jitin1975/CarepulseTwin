from pathlib import Path
import numpy as np,pandas as pd
out=Path('data/eicu');out.mkdir(parents=True,exist_ok=True);rng=np.random.default_rng(0);patients=[];rows=[]
for pid in range(1,31):
    expired=pid<=12; patients.append({'patientunitstayid':pid,'unitdischargeoffset':35*60,'unitdischargestatus':'Expired' if expired else 'Alive'})
    for h in range(40):
        frac=max(0,(h-15)/20) if expired else 0
        rows.append({'patientunitstayid':pid,'observationoffset':h*60,'heartrate':75+25*frac+rng.normal(0,1),'spo2':97-8*frac+rng.normal(0,.2),'systemicsystolic':120-12*frac+rng.normal(0,1),'systemicdiastolic':78-5*frac+rng.normal(0,.7),'temperature':36.8+.7*frac+rng.normal(0,.03),'respiration':16+10*frac+rng.normal(0,.5)})
pd.DataFrame(patients).to_csv(out/'patient.csv',index=False);pd.DataFrame(rows).to_csv(out/'vitalPeriodic.csv',index=False)
print('fixture created under data/eicu')
