import argparse,asyncio,random
from datetime import datetime,timezone
import httpx
async def main():
 p=argparse.ArgumentParser();p.add_argument('--api',default='http://localhost:8000');p.add_argument('--patient-id',default='P001');p.add_argument('--interval',type=float,default=1);p.add_argument('--deteriorate-after',type=int,default=45);a=p.parse_args()
 async with httpx.AsyncClient(timeout=10) as c:
  for step in range(1000):
   f=min(max(0,step-a.deteriorate_after)/60,1);d={'patient_id':a.patient_id,'ts':datetime.now(timezone.utc).isoformat(),'heart_rate':76+random.gauss(0,2)+35*f,'spo2':97+random.gauss(0,.4)-10*f,'systolic_bp':120+random.gauss(0,3)-8*f,'diastolic_bp':78+random.gauss(0,2)-4*f,'temperature':36.8+random.gauss(0,.05)+.8*f,'respiratory_rate':16+random.gauss(0,1)+14*f}
   try:r=await c.post(f'{a.api}/api/v1/ingest',json=d);print(step,r.status_code,r.json())
   except Exception as e:print('error',e)
   await asyncio.sleep(a.interval)
if __name__=='__main__':asyncio.run(main())
