import os,asyncio,json
from fastapi import FastAPI,WebSocket,WebSocketDisconnect,HTTPException,Depends
from pydantic import BaseModel,Field
from aiokafka import AIOKafkaProducer,AIOKafkaConsumer
from redis.asyncio import Redis
from sqlalchemy import create_engine,text
from backend.core import RiskEngine,screen,severity,explain
from backend.auth import require_role

TOPIC=os.getenv('KAFKA_TOPIC','carepulse.vitals'); BOOT=os.getenv('KAFKA_BOOTSTRAP_SERVERS','localhost:9092')
MODEL=os.getenv('MODEL_PATH','ml/artifacts/carepulse_lstm.pt')
app=FastAPI(title='CarePulse Twin — eICU')
redis=Redis.from_url(os.getenv('REDIS_URL','redis://localhost:6379/0'),decode_responses=True)
engine=create_engine(f"postgresql+psycopg://{os.getenv('POSTGRES_USER','carepulse')}:{os.getenv('POSTGRES_PASSWORD','carepulse')}@{os.getenv('POSTGRES_HOST','localhost')}:{os.getenv('POSTGRES_PORT','5432')}/{os.getenv('POSTGRES_DB','carepulse')}",pool_pre_ping=True)
risk=RiskEngine(MODEL); producer=None; sockets={}
class Vital(BaseModel):
    patient_id:str=Field(min_length=1,max_length=64); ts:str
    heart_rate:float;spo2:float;systolic_bp:float;diastolic_bp:float;temperature:float;respiratory_rate:float

def insert_vital(v):
    with engine.begin() as c:c.execute(text('INSERT INTO vitals(patient_id,ts,heart_rate,spo2,systolic_bp,diastolic_bp,temperature,respiratory_rate,anomaly_flags) VALUES(:patient_id,:ts,:heart_rate,:spo2,:systolic_bp,:diastolic_bp,:temperature,:respiratory_rate,CAST(:flags AS jsonb)) ON CONFLICT(patient_id,ts) DO NOTHING'),{**v,'flags':json.dumps(v.get('flags',[]))})
def insert_audit(actor,action,pid,meta='{}'):
    with engine.begin() as c:c.execute(text('INSERT INTO audit_log(actor,action,patient_id,metadata) VALUES(:actor,:action,:pid,CAST(:meta AS jsonb))'),{'actor':actor,'action':action,'pid':pid,'meta':meta})
def insert_alert(a):
    with engine.begin() as c:c.execute(text('INSERT INTO alerts(patient_id,ts,severity,risk,factors,message) VALUES(:patient_id,:ts,:severity,:risk,CAST(:factors AS jsonb),:message)'),{**a,'factors':json.dumps(a['factors'])})
async def process(v):
    insert_vital(v); insert_audit('kafka-consumer','vital_processed',v['patient_id']); r,w=risk.score(v['patient_id'],v); sev=severity(r); factors=explain(v,w)
    state={'patient_id':v['patient_id'],'ts':v['ts'],'risk':r,'severity':sev,'window':len(w),'model_available':risk.available and len(w)>=risk.seq_len,'vitals':{k:v[k] for k in ['heart_rate','spo2','systolic_bp','diastolic_bp','temperature','respiratory_rate']},'factors':factors}
    await redis.set('state:'+v['patient_id'],json.dumps(state))
    for ws in list(sockets.get(v['patient_id'],set())):
        try: await ws.send_json({'type':'state','data':state})
        except: sockets[v['patient_id']].discard(ws)
    if sev!='LOW':
        a={'patient_id':v['patient_id'],'ts':v['ts'],'severity':sev,'risk':r,'factors':factors,'message':'; '.join(factors)}; insert_alert(a)
        for ws in list(sockets.get(v['patient_id'],set())):
            try: await ws.send_json({'type':'alert','data':a})
            except: sockets[v['patient_id']].discard(ws)
        insert_audit('alert-engine','alert_created',v['patient_id'],json.dumps({'severity':sev,'risk':r}))
async def consume():
    c=AIOKafkaConsumer(TOPIC,bootstrap_servers=BOOT,group_id='carepulse-inference',auto_offset_reset='latest',value_deserializer=lambda x:json.loads(x.decode())); await c.start()
    try:
        async for msg in c: await process(msg.value)
    finally: await c.stop()
@app.on_event('startup')
async def startup():
    global producer; producer=AIOKafkaProducer(bootstrap_servers=BOOT,value_serializer=lambda x:json.dumps(x).encode()); await producer.start(); app.state.consumer=asyncio.create_task(consume())
@app.on_event('shutdown')
async def shutdown():
    app.state.consumer.cancel(); await producer.stop(); await redis.aclose()
@app.get('/health')
async def health(): return {'status':'ok','model_available':risk.available,'kafka_topic':TOPIC}
@app.post('/api/v1/ingest')
async def ingest(v:Vital, user=Depends(require_role('doctor','patient'))):
    d=v.model_dump(); ok,flags=screen(d); d['flags']=flags
    if not ok:return {'accepted':False,'flags':flags}
    await producer.send_and_wait(TOPIC,d); return {'accepted':True,'flags':flags}
@app.get('/api/v1/patients/{pid}/state')
async def get_state(pid, user=Depends(require_role('doctor','patient'))):
    x=await redis.get('state:'+pid)
    if not x: raise HTTPException(404,'No current state')
    return json.loads(x)
@app.get('/api/v1/patients/{pid}/alerts')
async def get_alerts(pid, user=Depends(require_role('doctor','patient'))):
    with engine.begin() as c:
        rows=c.execute(text('SELECT patient_id,ts,severity,risk,factors,message FROM alerts WHERE patient_id=:p ORDER BY ts DESC LIMIT 50'),{'p':pid}).mappings().all()
    return [dict(r) for r in rows]

@app.websocket('/ws/patients/{pid}')
async def ws(w:WebSocket,pid:str):
    await w.accept(); sockets.setdefault(pid,set()).add(w)
    try:
        while True: await w.receive_text()
    except WebSocketDisconnect: pass
    finally: sockets.get(pid,set()).discard(w)
