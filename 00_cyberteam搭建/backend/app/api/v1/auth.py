"""
JWT Auth Endpoints — uses existing AuthService from app.auth.jwt
<!--zh
JWT 认证接口：登录/注册/Token刷新/当前用户
-->
"""
from __future__ import annotations

from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth.jwt import AuthService
from app.config import settings

# ─── Singleton ─────────────────────────────────────────────────────────────────

_auth_service = AuthService()

# ─── Mock user DB ──────────────────────────────────────────────────────────────
# Replace with real DB in production

_MOCK_USERS = {
    "admin": {
        "username": "admin",
        "hashed_password": _auth_service.hash_password("admin123"),
        "email": "admin@cyberteam.ai",
        "disabled": False,
        "org_id": "cyberteam",
        "role": "admin",
    },
    "demo": {
        "username": "demo",
        "hashed_password": _auth_service.hash_password("demo123"),
        "email": "demo@cyberteam.ai",
        "disabled": False,
        "org_id": "cyberteam",
        "role": "user",
    },
}


def get_user(username: str) -> Optional[dict]:
    return _MOCK_USERS.get(username)


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user(username)
    if not user:
        return None
    if not _auth_service.verify_password(password, user["hashed_password"]):
        return None
    return user


# ─── Pydantic models ──────────────────────────────────────────────────────────


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: bool = False
    org_id: str = "cyberteam"
    role: str = "user"


class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


# ─── OAuth2 scheme ───────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = _auth_service.verify_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return User(
        username=user["username"],
        email=user.get("email"),
        disabled=user.get("disabled", False),
        org_id=user.get("org_id", "cyberteam"),
        role=user.get("role", "user"),
    )


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ─── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    <!--zh
    登录：用户名+密码，返回 JWT token
    -->
    Login with username and password, returns JWT access token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = _auth_service.create_token(
        data={"sub": user["username"], "org": user.get("org_id", "cyberteam"), "role": user.get("role", "user")}
    )
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return Token(access_token=access_token, expires_in=expire_seconds)


@router.post("/register", response_model=User)
async def register(user_create: UserCreate) -> User:
    """
    <!--zh
    注册新用户（开发环境可用，生产需加管理员权限）
    -->
    Register a new user (dev only — add admin gate in production).
    """
    if user_create.username in _MOCK_USERS:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = _auth_service.hash_password(user_create.password)
    _MOCK_USERS[user_create.username] = {
        "username": user_create.username,
        "hashed_password": hashed,
        "email": user_create.email or f"{user_create.username}@cyberteam.ai",
        "disabled": False,
        "org_id": "cyberteam",
        "role": "user",
    }
    return User(
        username=user_create.username,
        email=user_create.email,
        disabled=False,
        org_id="cyberteam",
        role="user",
    )


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    <!--zh
    获取当前登录用户信息
    -->
    Get current authenticated user info.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user),
) -> Token:
    """
    <!--zh
    刷新 Token
    -->
    Refresh access token.
    """
    access_token = _auth_service.create_token(
        data={"sub": current_user.username, "org": current_user.org_id, "role": current_user.role}
    )
    expire_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return Token(access_token=access_token, expires_in=expire_seconds)
