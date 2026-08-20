import argparse,asyncio,time,uuid,httpx
from datetime import datetime,timezone
async def main():
 p=argparse.ArgumentParser();p.add_argument('--api',default='http://localhost:8000');p.add_argument('--patient',default='BENCH');p.add_argument('--n',type=int,default=20);a=p.parse_args();times=[]
 async with httpx.AsyncClient(timeout=10) as c:
  for _ in range(a.n):
   ts=datetime.now(timezone.utc).isoformat(); payload={'patient_id':a.patient,'ts':ts,'heart_rate':75,'spo2':97,'systolic_bp':120,'diastolic_bp':78,'temperature':36.8,'respiratory_rate':16}
   t=time.perf_counter(); r=await c.post(a.api+'/api/v1/ingest',json=payload); r.raise_for_status()
   while time.perf_counter()-t<10:
    try:
     s=(await c.get(a.api+f'/api/v1/patients/{a.patient}/state')).json()
     if s.get('ts')==ts: break
    except Exception: pass
    await asyncio.sleep(.01)
   else: raise RuntimeError('state did not arrive within 10 seconds')
   times.append((time.perf_counter()-t)*1000)
 times.sort();print('end_to_end_ms_p50=',times[len(times)//2]);print('end_to_end_ms_p95=',times[max(0,int(.95*len(times))-1)]);print('end_to_end_ms_mean=',sum(times)/len(times));print('This measures API ingest -> Kafka -> consumer -> DB/Redis -> state visibility.')
if __name__=='__main__':asyncio.run(main())
