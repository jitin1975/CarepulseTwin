from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
import jwt
from backend.config import settings
bearer=HTTPBearer(auto_error=False)
def require_role(roles=None):
 roles=roles or []
 async def dep(creds:HTTPAuthorizationCredentials=Depends(bearer)):
  if settings.auth_disabled:return {'sub':'local-demo','role':'doctor'}
  if not creds:raise HTTPException(401,'Missing bearer token')
  try:p=jwt.decode(creds.credentials,settings.jwt_secret,algorithms=[settings.jwt_algorithm])
  except jwt.PyJWTError:raise HTTPException(401,'Invalid token')
  if roles and p.get('role') not in roles:raise HTTPException(403,'Insufficient role')
  return p
 return dep
