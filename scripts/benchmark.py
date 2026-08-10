import argparse,asyncio,statistics,time,httpx
from datetime import datetime,timezone
async def main():
 p=argparse.ArgumentParser();p.add_argument('--api',default='http://localhost:8000');p.add_argument('--n',type=int,default=100);a=p.parse_args();lat=[]
 async with httpx.AsyncClient(timeout=10) as c:
  for _ in range(a.n):
   d={'patient_id':'P001','ts':datetime.now(timezone.utc).isoformat(),'heart_rate':75,'spo2':97,'systolic_bp':120,'diastolic_bp':78,'temperature':36.8,'respiratory_rate':16};t=time.perf_counter();r=await c.post(f'{a.api}/api/v1/ingest',json=d);r.raise_for_status();lat.append((time.perf_counter()-t)*1000)
 print('p50',statistics.median(lat),'p95',sorted(lat)[int(.95*len(lat))-1],'mean',statistics.mean(lat));print('This measures API publish latency, not full edge-to-alert latency.')
if __name__=='__main__':asyncio.run(main())
