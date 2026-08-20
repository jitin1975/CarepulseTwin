from collections import defaultdict, deque
import numpy as np, torch
from ml.model import CarePulseLSTM
FEATURES=['heart_rate','spo2','systolic_bp','diastolic_bp','temperature','respiratory_rate']
class RiskEngine:
    def __init__(self,path):
        self.windows=defaultdict(lambda:deque(maxlen=24)); self.available=False; self.threshold=.5
        try:
            ck=torch.load(path,map_location='cpu',weights_only=False); self.model=CarePulseLSTM(n=len(ck.get('feature_names',FEATURES))); self.model.load_state_dict(ck['state_dict']); self.model.eval(); self.mean=np.asarray(ck['mean'],dtype=np.float32); self.std=np.asarray(ck['std'],dtype=np.float32); self.seq_len=int(ck['seq_len']); self.threshold=float(ck.get('threshold',.5)); self.available=True
        except Exception as e: self.model=None; self.seq_len=24; print('model unavailable:',e)
    def score(self,pid,v):
        self.windows[pid].append(np.array([v[x] for x in FEATURES],dtype=np.float32)); w=list(self.windows[pid])
        if self.available and len(w)==self.seq_len:
            x=(np.asarray(w)-self.mean)/self.std
            with torch.no_grad(): r=float(torch.sigmoid(self.model(torch.tensor(x[None],dtype=torch.float32))).item())
        else:
            r=min((.30 if v['spo2']<92 else 0)+(.25 if v['spo2']<88 else 0)+(.20 if v['respiratory_rate']>24 else 0)+(.15 if v['heart_rate']>120 else 0)+(.10 if v['temperature']>38.5 else 0),.99)
        return r,w

def severity(r): return 'CRITICAL' if r>=.85 else 'HIGH' if r>=.65 else 'MEDIUM' if r>=.40 else 'LOW'
def explain(v,w):
    f=[]
    if v['spo2']<92:f.append(f"SpO2 is {v['spo2']:.1f}%")
    if v['respiratory_rate']>24:f.append(f"respiratory rate is {v['respiratory_rate']:.1f}/min")
    if v['heart_rate']>110:f.append(f"heart rate is {v['heart_rate']:.1f} bpm")
    if v['temperature']>38:f.append(f"temperature is {v['temperature']:.1f} C")
    if len(w)>=5:
        if w[-1][1]<w[-5][1]-2:f.append(f"SpO2 declined from {w[-5][1]:.1f}% to {w[-1][1]:.1f}%")
        if w[-1][5]>w[-5][5]+4:f.append('respiratory rate has an upward trend')
        if w[-1][0]>w[-5][0]+15:f.append('heart rate has an upward trend')
    return f[:5] or ['No dominant abnormal trend detected']
def screen(v):
    ranges={'heart_rate':(20,250),'spo2':(50,100),'systolic_bp':(40,300),'diastolic_bp':(20,200),'temperature':(25,45),'respiratory_rate':(2,80)}; flags=[]
    for k,(lo,hi) in ranges.items():
        if not lo<=float(v[k])<=hi: flags.append(k+'_out_of_range')
    if v['spo2']<90: flags.append('low_spo2')
    if v['respiratory_rate']>30: flags.append('high_respiratory_rate')
    return not any(x.endswith('_out_of_range') for x in flags),sorted(set(flags))
