import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ALGORITHM = "HS256"

USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "reader": {"password": "reader123", "role": "reader"},
}

def create_token(username, role, expires_minutes=30):
    now = datetime.now(timezone.utc)
    payload = {"sub": username, "role": role, "iat": now, "exp": now + timedelta(minutes=expires_minutes)}
    return jwt.encode(payload, JWT_SECRET, algorithm=ALGORITHM)

def decode_token(token):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid or expired token", headers={"WWW-Authenticate": "Bearer"}) from exc
