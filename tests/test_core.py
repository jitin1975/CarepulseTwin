from backend.core import screen,severity,explain

def v(**kw):
    x={'heart_rate':75,'spo2':97,'systolic_bp':120,'diastolic_bp':78,'temperature':36.8,'respiratory_rate':16};x.update(kw);return x

def test_screen():
    assert screen(v())[0]
    ok,flags=screen(v(spo2=101)); assert not ok and 'spo2_out_of_range' in flags

def test_severity():
    assert severity(.1)=='LOW'; assert severity(.5)=='MEDIUM'; assert severity(.7)=='HIGH'; assert severity(.9)=='CRITICAL'

def test_explain_trend():
    h=[[75,97,120,78,36.8,16] for _ in range(4)]+[[100,90,120,78,36.8,22]]
    f=explain(v(heart_rate=100,spo2=90,respiratory_rate=22),h)
    assert any('SpO2' in x for x in f)
