"""JWT 认证服务 - 抄 Magic。

核心功能：
- JWT Token 创建与验证
- FastAPI 依赖注入集成
- 支持多租户（org_id）
- 支持角色（admin/user/guest）
- 可选认证（未携带 token 时返回 guest 身份）

安全设计：
- Token 有效期 24 小时
- 使用 HS256 算法签名
- 生产环境必须更换 SECRET_KEY
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import logging

log = logging.getLogger("cyberteam.auth")

# 尝试导入 jose，如果不存在则提供降级方案
try:
    from jose import jwt, JWTError, ExpiredSignatureError
    _JOSE_AVAILABLE = True
except ImportError:
    _JOSE_AVAILABLE = False
    log.warning("python-jose not installed, JWT auth will be in mock mode")

security = HTTPBearer(auto_error=False)


class AuthService:
    """JWT 认证服务。

    用法:
        auth = AuthService()
        token = auth.create_token(user_id="user1", org_id="org1", role="admin")
        payload = auth.verify_token(token)
    """

    SECRET_KEY = os.getenv("JWT_SECRET", "cyberteam-secret-key-change-in-production")
    ALGORITHM = "HS256"
    TOKEN_EXPIRE_HOURS = 24

    def create_token(
        self,
        user_id: str,
        org_id: str = "default",
        role: str = "user",
        extra: Optional[dict] = None,
    ) -> str:
        """创建 JWT Token。

        Args:
            user_id: 用户ID
            org_id: 组织ID（多租户）
            role: 用户角色（admin/user/guest）
            extra: 额外 payload 数据

        Returns:
            JWT Token 字符串
        """
        expire = datetime.utcnow() + timedelta(hours=self.TOKEN_EXPIRE_HOURS)
        issued_at = datetime.utcnow()
        payload = {
            "sub": user_id,
            "org": org_id,
            "role": role,
            "exp": expire.isoformat(),
            "iat": issued_at.isoformat(),
        }
        if extra:
            payload.update(extra)

        if not _JOSE_AVAILABLE:
            # 降级模式：返回 base64 编码的简单 token
            import base64
            import json
            return base64.b64encode(json.dumps(payload).encode()).decode()

        return jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def verify_token(self, token: str) -> dict:
        """验证 JWT Token。

        Args:
            token: JWT Token 字符串

        Returns:
            解码后的 payload 字典

        Raises:
            HTTPException: Token 无效或过期
        """
        if not _JOSE_AVAILABLE:
            # 降级模式：base64 解码
            try:
                import base64
                import json
                return json.loads(base64.b64decode(token).decode())
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """FastAPI 依赖注入：获取当前用户。

    未携带 Token 时返回 guest 身份，不拒绝请求。

    Returns:
        用户信息字典 {"sub": user_id, "org": org_id, "role": role}
    """
    if not credentials:
        return {"sub": "anonymous", "org": "default", "role": "guest"}

    auth = AuthService()
    return auth.verify_token(credentials.credentials)


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """FastAPI 依赖注入：强制要求认证。

    未携带 Token 时返回 401。

    Returns:
        用户信息字典
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    auth = AuthService()
    return auth.verify_token(credentials.credentials)


async def require_admin(
    user: dict = Depends(get_current_user),
) -> dict:
    """FastAPI 依赖注入：要求管理员角色。

    Returns:
        管理员用户信息字典

    Raises:
        HTTPException: 非管理员
    """
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user
