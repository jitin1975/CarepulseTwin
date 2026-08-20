import argparse,os,jwt
from datetime import datetime,timedelta,timezone
p=argparse.ArgumentParser();p.add_argument('--sub',default='demo-doctor');p.add_argument('--role',choices=['doctor','patient'],default='doctor');a=p.parse_args()
print(jwt.encode({'sub':a.sub,'role':a.role,'exp':datetime.now(timezone.utc)+timedelta(hours=8)},os.getenv('JWT_SECRET','change-me'),algorithm='HS256'))
