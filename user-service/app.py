import os
import secrets
import redis
from fastapi import FastAPI, Header, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel, Field

store = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"), decode_responses=True)
passwords = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="User Service", version="1.0.0")

class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=6, max_length=72)

@app.get("/health")
def health():
    store.ping()
    return {"status": "healthy", "service": "user-service"}

@app.post("/users/register", status_code=201)
def register(payload: Credentials):
    key = f"user:{payload.username.lower()}"
    if store.exists(key):
        raise HTTPException(409, "Username already exists")
    store.set(key, passwords.hash(payload.password))
    return {"message": "User registered", "username": payload.username.lower()}

@app.post("/users/login")
def login(payload: Credentials):
    username = payload.username.lower()
    saved_hash = store.get(f"user:{username}")
    if not saved_hash or not passwords.verify(payload.password, saved_hash):
        raise HTTPException(401, "Invalid username or password")
    token = secrets.token_urlsafe(32)
    store.setex(f"session:{token}", 86400, username)
    return {"token": token, "username": username}

@app.get("/users/me")
def me(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    token = authorization.removeprefix("Bearer ")
    username = store.get(f"session:{token}")
    if not username:
        raise HTTPException(401, "Invalid or expired token")
    return {"username": username}

