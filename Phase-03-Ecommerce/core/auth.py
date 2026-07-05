from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

#-----converts a plain password into a secure hash.------#

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

#------ checks whether the entered password matches the stored hash. ------#

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

#------  -------#

def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire  = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload.update({"exp": expire})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

#------ checks and decodes a JWT --------#

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])