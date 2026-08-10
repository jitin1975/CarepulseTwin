from sqlalchemy import create_engine,text
from backend.config import settings
engine=create_engine(settings.postgres_dsn,pool_pre_ping=True)
def save_vital(r):
 with engine.begin() as c:
  c.execute(text("INSERT INTO patients(patient_id,display_name) VALUES (:p,:p) ON CONFLICT DO NOTHING"),{'p':r['patient_id']})
  c.execute(text("""INSERT INTO vitals(patient_id,ts,heart_rate,spo2,systolic_bp,diastolic_bp,temperature,respiratory_rate,accepted,anomaly_flags) VALUES (:patient_id,:ts,:heart_rate,:spo2,:systolic_bp,:diastolic_bp,:temperature,:respiratory_rate,:accepted,CAST(:flags AS jsonb)) ON CONFLICT (patient_id,ts) DO NOTHING"""),{**r,'flags':'['+','.join('"'+x+'"' for x in r.get('anomaly_flags',[]))+']'})
def save_alert(a):
 with engine.begin() as c:c.execute(text("INSERT INTO alerts(patient_id,ts,severity,risk,factors,message) VALUES (:patient_id,:ts,:severity,:risk,CAST(:factors AS jsonb),:message)"),{**a,'factors':'['+','.join('"'+x.replace('"','\\"')+'"' for x in a['factors'])+']'})
def recent_vitals(p,limit=30):
 with engine.begin() as c: rows=c.execute(text("SELECT patient_id,ts,heart_rate,spo2,systolic_bp,diastolic_bp,temperature,respiratory_rate FROM vitals WHERE patient_id=:p ORDER BY ts DESC LIMIT :lim"),{'p':p,'lim':limit}).mappings().all()
 return [dict(x) for x in reversed(rows)]
def recent_alerts(p,limit=20):
 with engine.begin() as c: rows=c.execute(text("SELECT patient_id,ts,severity,risk,factors,message FROM alerts WHERE patient_id=:p ORDER BY ts DESC LIMIT :lim"),{'p':p,'lim':limit}).mappings().all()
 return [dict(x) for x in rows]
