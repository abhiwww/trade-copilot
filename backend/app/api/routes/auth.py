from fastapi import APIRouter, HTTPException, Depends, Response, Cookie, Request
from pydantic import BaseModel, EmailStr
from typing import Optional
import bcrypt
import uuid
import base64
from app.core import repository as repo_module
from app.models.trade_models import User, Organization
from app.core.sessions import session_store
from app.core.ratelimit import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    org_name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProfileUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None

async def get_current_user(request: Request, session_token: Optional[str] = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session = session_store.get_session(session_token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    ua = request.headers.get("user-agent", "")
    ip = request.client.host if request.client else "unknown"
    if session["ua_hash"] != hash(ua) or session["ip"] != ip:
        session_store.delete_session(session_token)
        raise HTTPException(status_code=401, detail="Session anomaly detected; please login again")

    repo = repo_module.RepositoryContainer(db)
    user = await repo.users.get_by_id(session["user_id"])
    if not user:
        session_store.delete_session(session_token)
        raise HTTPException(status_code=401, detail="User no longer exists")

    session_store.touch_session(session_token)
    return user

def serialize_current_user(user: User):
    # Note: In a real async app, this would be async, but we handle the org fetch inside the route
    return {
        "user_id": user.user_id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "name": f"{user.first_name} {user.last_name}".strip(),
        "display_name": f"{user.first_name} {user.last_name}".strip(),
        "avatar_url": None,
        "role": user.role,
        "job_title": user.job_title,
        "phone": user.phone,
        "timezone": user.timezone,
        "language": user.language,
        "org_id": user.org_id,
        "organization": {
            "org_id": user.org_id,
            "name": "Loading...", # Handled by frontend or specific endpoint
            "plan": "Enterprise",
        },
    }

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    repo = repo_module.RepositoryContainer(db)
    if await repo.users.get_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    org_id = str(uuid.uuid4())
    organization = Organization(
        org_id=org_id,
        name=req.org_name,
        plan="Enterprise"
    )
    await repo.orgs.save(org_id, organization)

    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(req.password.encode('utf-8'), salt)
    hashed_pw_str = base64.b64encode(hashed_pw).decode('utf-8')

    user_id = str(uuid.uuid4())
    user = User(
        user_id=user_id,
        email=req.email,
        first_name=req.first_name,
        last_name=req.last_name,
        password_hash=hashed_pw_str,
        org_id=org_id,
        role="Owner"
    )
    await repo.users.save(user_id, user)

    return {"message": "User registered successfully", "user_id": user_id}

@router.post("/login")
async def login(req: LoginRequest, response: Response, request: Request, db: AsyncSession = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    limit_key = f"login:{ip}:{req.email}"
    allowed, retry_after = limiter.check_limit(limit_key, limit=5, window=60)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"Too many login attempts. Please try again in {retry_after}s."
        )

    repo = repo_module.RepositoryContainer(db)
    user = await repo.users.get_by_email(req.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    try:
        hashed_bytes = base64.b64decode(user.password_hash)
        if not bcrypt.checkpw(req.password.encode('utf-8'), hashed_bytes):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = session_store.create_session(
        user_id=user.user_id,
        org_id=user.org_id,
        user_agent=request.headers.get("user-agent", ""),
        ip=request.client.host if request.client else "unknown"
    )

    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=86400 * 7
    )
    return {"message": "Login successful", "user": serialize_current_user(user)}

@router.post("/logout")
async def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    if session_token:
        session_store.delete_session(session_token)
    response.delete_cookie("session_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return serialize_current_user(user)

@router.put("/me")
async def update_me(req: ProfileUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if req.email and req.email != user.email:
        repo = repo_module.RepositoryContainer(db)
        existing_user = await repo.users.get_by_email(req.email)
        if existing_user and existing_user.user_id != user.user_id:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = req.email

    for field in ("first_name", "last_name", "job_title", "phone", "timezone", "language"):
        value = getattr(req, field)
        if value is not None:
            setattr(user, field, value.strip() if isinstance(value, str) else value)

    repo = repo_module.RepositoryContainer(db)
    await repo.users.save(user.user_id, user)
    return serialize_current_user(user)
