"""Dependency injection for API routes."""
from __future__ import annotations

from typing import AsyncGenerator, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.database import async_sessionmaker
from app.auth.jwt import AuthService

security = HTTPBearer()
auth_service = AuthService()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session."""
    async with async_sessionmaker() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Dependency to get current user from JWT token."""
    token = credentials.credentials
    try:
        payload = auth_service.verify_token(token)
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[dict]:
    """Optional user dependency for public endpoints."""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
