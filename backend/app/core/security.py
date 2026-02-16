from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings
from typing import Any
import bcrypt

def create_token(data: dict[str, Any], expires_delta: timedelta) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def get_password_hash(password: str) -> bytes:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password=password_bytes, salt=salt)

def verify_password(plain: str, hashed: bytes) -> bool:
    plain_bytes = plain.encode("utf-8")
    return bcrypt.checkpw(password=plain_bytes, hashed_password=hashed)

def decode_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str | None = payload.get("sub")
        return user_id
    except JWTError:
        return None
