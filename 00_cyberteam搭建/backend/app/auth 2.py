"""
Auth module - JWT based authentication.
<!--zh
JWT 认证模块：登录/注册/Token刷新/密码验证
-->
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ─── Config ───────────────────────────────────────────────────────────────────

SECRET_KEY = os.getenv("JWT_SECRET", "cyberteam-dev-secret-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ─── Password hashing ─────────────────────────────────────────────────────────

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ─── Mock user store ──────────────────────────────────────────────────────────
# In production, replace with real DB (SQLAlchemy / Prisma / Drizzle)

_USERS_DB: dict[str, dict] = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "email": "admin@cyberteam.ai",
        "disabled": False,
        "org_id": "cyberteam",
        "role": "admin",
    },
    "demo": {
        "username": "demo",
        "hashed_password": pwd_context.hash("demo123"),
        "email": "demo@cyberteam.ai",
        "disabled": False,
        "org_id": "cyberteam",
        "role": "user",
    },
}

# ─── Pydantic models ──────────────────────────────────────────────────────────


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None


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


class UserInDB(User):
    hashed_password: str


# ─── Helpers ───────────────────────────────────────────────────────────────────


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username: str) -> Optional[UserInDB]:
    if username in _USERS_DB:
        return UserInDB(**_USERS_DB[username])
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─── OAuth2 scheme ───────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return User(
        username=user.username,
        email=user.email,
        disabled=user.disabled,
        org_id=user.org_id,
        role=user.role,
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ─── Router ────────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """
    <!--zh
    登录接口：用户名+密码登录，返回 JWT token
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
    access_token = create_access_token(
        data={"sub": user.username, "org": user.org_id, "role": user.role}
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=User)
async def register(user_create: UserCreate) -> User:
    """
    <!--zh
    注册接口：创建新用户（开发环境可用，生产应加管理员权限）
    -->
    Register a new user (dev only, add admin gate in production).
    """
    if user_create.username in _USERS_DB:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = get_password_hash(user_create.password)
    _USERS_DB[user_create.username] = {
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
async def read_users_me(current_user: User = Depends(get_current_active_user)) -> User:
    """
    <!--zh
    获取当前登录用户信息
    -->
    Get current authenticated user info.
    """
    return current_user


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: User = Depends(get_current_active_user)) -> Token:
    """
    <!--zh
    刷新 Token：延长会话有效期
    -->
    Refresh access token.
    """
    access_token = create_access_token(
        data={"sub": current_user.username, "org": current_user.org_id, "role": current_user.role}
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
