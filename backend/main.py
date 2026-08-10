import asyncio,json,uuid
from fastapi import FastAPI,Depends,WebSocket,WebSocketDisconnect,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from backend.config import settings
from backend.schemas import VitalReading,IngestResponse
from backend.kafka_service import KafkaService
from backend.auth import require_role
from backend.risk_engine import RiskEngine,severity_for
from backend.explain import explain
from backend.db import save_vital,save_alert,recent_vitals,recent_alerts
from edge.validator import EdgeValidator
app=FastAPI(title='CarePulse Twin',version='1.0.0');app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
kafka=KafkaService();redis=Redis.from_url(settings.redis_url,decode_responses=True);edge=EdgeValidator();risk_engine=RiskEngine(settings.model_path);connections={}
async def broadcast(p,payload):
 dead=[]
 for ws in connections.get(p,set()):
  try:await ws.send_json(payload)
  except Exception:dead.append(ws)
 for ws in dead:connections[p].discard(ws)
async def process(e):
 p=e['patient_id'];save_vital(e);rows=recent_vitals(p,30);h=[[x['heart_rate'],x['spo2'],x['systolic_bp'],x['diastolic_bp'],x['temperature'],x['respiratory_rate']] for x in rows];risk,count=risk_engine.score(p,e);sev=severity_for(risk);f=explain(e,h)
 state={'patient_id':p,'ts':e['ts'],'risk':round(risk,4),'severity':sev,'factors':f,'vitals':{k:e[k] for k in ['heart_rate','spo2','systolic_bp','diastolic_bp','temperature','respiratory_rate']},'model_available':risk_engine.available and count>=risk_engine.seq_len}
 await redis.set(f'state:{p}',json.dumps(state,default=str));await broadcast(p,{'type':'state','data':state})
 if sev!='LOW':
  a={'patient_id':p,'ts':e['ts'],'severity':sev,'risk':risk,'factors':f,'message':f"{sev} early-warning risk. Contributing factors: {'; '.join(f)}"};save_alert(a);await broadcast(p,{'type':'alert','data':a})
@app.on_event('startup')
async def startup():await kafka.start();app.state.consumer_task=asyncio.create_task(kafka.consume(process))
@app.on_event('shutdown')
async def shutdown():app.state.consumer_task.cancel();await kafka.stop();await redis.close()
@app.get('/health')
async def health():return {'status':'ok','model_available':risk_engine.available,'kafka':settings.kafka_bootstrap}
@app.post('/api/v1/ingest',response_model=IngestResponse)
async def ingest(reading:VitalReading,user=Depends(require_role(['doctor','patient']))):
 d=reading.model_dump(mode='json');res=edge.validate(d);d['accepted']=res.accepted;d['anomaly_flags']=res.flags;eid=str(uuid.uuid4())
 if not res.accepted:return IngestResponse(accepted=False,anomaly_flags=res.flags,event_id=eid)
 d['event_id']=eid;await kafka.publish(d);return IngestResponse(accepted=True,anomaly_flags=res.flags,event_id=eid)
@app.get('/api/v1/patients/{patient_id}/state')
async def state(patient_id,user=Depends(require_role(['doctor','patient']))):
 raw=await redis.get(f'state:{patient_id}');
 if not raw:raise HTTPException(404,'No current state')
 return json.loads(raw)
@app.get('/api/v1/patients/{patient_id}/vitals')
async def vitals(patient_id,limit:int=30,user=Depends(require_role(['doctor','patient']))):return recent_vitals(patient_id,min(max(limit,1),200))
@app.get('/api/v1/patients/{patient_id}/alerts')
async def alerts(patient_id,limit:int=20,user=Depends(require_role(['doctor','patient']))):return recent_alerts(patient_id,min(max(limit,1),100))
@app.websocket('/ws/patients/{patient_id}')
async def ws(websocket:WebSocket,patient_id):
 await websocket.accept();connections.setdefault(patient_id,set()).add(websocket)
 try:
  raw=await redis.get(f'state:{patient_id}')
  if raw:await websocket.send_json({'type':'state','data':json.loads(raw)})
  while True:await websocket.receive_text()
 except WebSocketDisconnect:pass
 finally:connections.get(patient_id,set()).discard(websocket)
