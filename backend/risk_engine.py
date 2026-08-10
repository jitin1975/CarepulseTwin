from collections import deque
import numpy as np,torch
from ml.model import CarePulseLSTM
class RiskEngine:
 def __init__(self,path,seq_len=30):
  self.seq_len=seq_len;self.windows={};self.model=CarePulseLSTM();self.available=False
  try:
   c=torch.load(path,map_location='cpu');self.model.load_state_dict(c['state_dict']);self.means=np.asarray(c['means'],dtype=np.float32);self.stds=np.asarray(c['stds'],dtype=np.float32);self.model.eval();self.available=True
  except Exception as e:
   print('Model unavailable:',e);self.means=np.array([75,97,120,78,36.8,16],dtype=np.float32);self.stds=np.array([12,1.5,12,9,.35,3.5],dtype=np.float32)
 def score(self,p,r):
  f=np.array([r['heart_rate'],r['spo2'],r['systolic_bp'],r['diastolic_bp'],r['temperature'],r['respiratory_rate']],dtype=np.float32);q=self.windows.setdefault(p,deque(maxlen=self.seq_len));q.append(f)
  if not self.available or len(q)<self.seq_len:
   risk=0
   if r['spo2']<92:risk+=.3
   if r['spo2']<88:risk+=.25
   if r['respiratory_rate']>24:risk+=.2
   if r['heart_rate']>120:risk+=.15
   if r['temperature']>38.5:risk+=.1
   return min(risk,.99),len(q)
  x=(np.stack(q)-self.means)/self.stds
  with torch.no_grad(): prob=torch.sigmoid(self.model(torch.tensor(x[None,...]))).item()
  return float(prob),len(q)
def severity_for(r): return 'CRITICAL' if r>=.85 else 'HIGH' if r>=.65 else 'MEDIUM' if r>=.40 else 'LOW'
