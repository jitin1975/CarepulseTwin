import numpy as np
def explain(r,h):
 f=[]
 if r['spo2']<92:f.append(f"SpO2 is low at {r['spo2']:.0f}%")
 if r['heart_rate']>110:f.append(f"heart rate is elevated at {r['heart_rate']:.0f} bpm")
 if r['respiratory_rate']>24:f.append(f"respiratory rate is elevated at {r['respiratory_rate']:.0f}/min")
 if r['temperature']>38:f.append(f"temperature is elevated at {r['temperature']:.1f}°C")
 if len(h)>=5:
  a=np.array(h[-5:],float)
  if a[-1,1]<a[0,1]-2:f.append(f"SpO2 declined from {a[0,1]:.0f}% to {a[-1,1]:.0f}%")
  if a[-1,5]>a[0,5]+4:f.append('respiratory rate shows a sustained upward trend')
  if a[-1,0]>a[0,0]+15:f.append('heart rate shows a sustained upward trend')
 return f[:5] or ['No dominant abnormal factor detected']
