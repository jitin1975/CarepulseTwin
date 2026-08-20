import argparse,pandas as pd
p=argparse.ArgumentParser();p.add_argument('--eicu-dir',required=True);p.add_argument('--n',type=int,default=10);a=p.parse_args();v=pd.read_csv(a.eicu_dir+'/vitalPeriodic.csv',usecols=['patientunitstayid']);print(v.patientunitstayid.value_counts().head(a.n))
