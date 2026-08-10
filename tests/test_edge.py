from edge.validator import EdgeValidator
def test_normal():
 r=EdgeValidator().validate({'heart_rate':75,'spo2':97,'systolic_bp':120,'diastolic_bp':78,'temperature':36.8,'respiratory_rate':16});assert r.accepted
def test_impossible():
 r=EdgeValidator().validate({'heart_rate':75,'spo2':101,'systolic_bp':120,'diastolic_bp':78,'temperature':36.8,'respiratory_rate':16});assert not r.accepted
