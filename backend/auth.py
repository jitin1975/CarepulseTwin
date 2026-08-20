import os, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security=HTTPBearer(auto_error=False)

def require_role(*roles):
    async def dep(c:HTTPAuthorizationCredentials=Depends(security)):
        if os.getenv('AUTH_DISABLED','true').lower()=='true': return {'sub':'local-demo','role':roles[0] if roles else 'doctor'}
        if not c: raise HTTPException(401,'Missing bearer token')
        try: p=jwt.decode(c.credentials,os.getenv('JWT_SECRET','change-me'),algorithms=['HS256'])
        except jwt.PyJWTError: raise HTTPException(401,'Invalid token')
        if roles and p.get('role') not in roles: raise HTTPException(403,'Insufficient role')
        return p
    return dep
