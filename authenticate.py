from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, Depends,status

SECRET_KEY = "SECRET_KEY"
pwd_context = CryptContext(schemes="bcrypt" , deprecated = "auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def generate_access_token(data : dict):
    info = data.copy()
    info['exp'] = datetime.utcnow() + timedelta(minutes=15)
    info.update()
    token = jwt.encode(info, SECRET_KEY, algorithm="HS256")
    return token

def generate_refresh_token(data : dict):
    info = data.copy()
    info['exp'] = datetime.utcnow() + timedelta(days=7)
    info.update()
    token = jwt.encode(info, SECRET_KEY, algorithm="HS256")
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except ExpiredSignatureError:
        return None
    except JWTError:
        return None
    return payload

def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing Token")
    return token

def get_email_from_token(token:str = Depends(get_token_from_cookie)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid token")
    return payload["email"]