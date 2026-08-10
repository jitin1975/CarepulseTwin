from dataclasses import dataclass
@dataclass
class EdgeResult:
    accepted: bool
    flags: list[str]
class EdgeValidator:
    def validate(self,r):
        flags=[]
        ranges={'heart_rate':(30,220),'spo2':(70,100),'systolic_bp':(60,240),'diastolic_bp':(30,160),'temperature':(32,43),'respiratory_rate':(5,60)}
        for k,(lo,hi) in ranges.items():
            if not lo <= float(r[k]) <= hi: flags.append(f'{k}_out_of_range')
        if r['spo2']<90: flags.append('low_spo2')
        if r['respiratory_rate']>30: flags.append('high_respiratory_rate')
        if r['heart_rate']>120 or r['heart_rate']<45: flags.append('abnormal_heart_rate')
        return EdgeResult(not any('out_of_range' in x for x in flags),sorted(set(flags)))
