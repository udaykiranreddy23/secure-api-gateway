import os
import uuid
import redis
import httpx
from fastapi import FastAPI, Depends, Header, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from app.security import USERS, create_token, decode_token
from app.rate_limit import RateLimiter
from app.audit import record

app = FastAPI(title="Secure API Gateway", version="1.0.0")
security = HTTPBearer(auto_error=False)

redis_client = redis.from_url(os.getenv("REDIS_URL","redis://localhost:6379/0"), decode_responses=True)
limiter = RateLimiter(redis_client)
UPSTREAM_URL = os.getenv("UPSTREAM_URL","http://localhost:9000")
DEMO_API_KEY = os.getenv("DEMO_API_KEY","demo-service-key")

class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)

def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security),
                 x_api_key: str | None = Header(None)):
    if x_api_key:
        if x_api_key != DEMO_API_KEY:
            raise HTTPException(401, "Invalid API key")
        return {"sub":"service-client","role":"service"}
    if not credentials:
        raise HTTPException(401, "Authentication required", headers={"WWW-Authenticate":"Bearer"})
    return decode_token(credentials.credentials)

def require_role(*roles):
    def dependency(user=Depends(current_user)):
        if user.get("role") not in roles:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return dependency

@app.middleware("http")
async def middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

@app.get("/health")
def health():
    return {"status":"ok","service":"gateway"}

@app.post("/auth/token")
def token(body: LoginRequest):
    user = USERS.get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(401, "Invalid credentials")
    return {"access_token":create_token(body.username,user["role"]),"token_type":"bearer","expires_in":1800}

@app.get("/admin/check")
def admin_check(user=Depends(require_role("admin"))):
    return {"message":"admin access granted","user":user["sub"]}

@app.get("/proxy/orders")
async def proxy_orders(request: Request, user=Depends(current_user)):
    identity = user.get("sub","unknown")
    if not limiter.allow(identity):
        raise HTTPException(429, "Rate limit exceeded")

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{UPSTREAM_URL}/orders", headers={"X-Request-ID":request_id})
    except httpx.RequestError as exc:
        record(request_id, identity, "GET", "/proxy/orders", 503)
        raise HTTPException(503, "Upstream unavailable") from exc

    record(request_id, identity, "GET", "/proxy/orders", response.status_code)
    return {"upstream_status":response.status_code,"request_id":request_id,"data":response.json()}
