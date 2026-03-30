"""认证中间件 - Header提取与租户识别。

提供:
- get_current_user: 强制认证，从 X-Company-ID Header 提取租户信息
- get_optional_user: 可选认证，用于公共端点
"""

from typing import Optional

from fastapi import Header, HTTPException, status, Depends


async def get_current_user(x_company_id: Optional[str] = Header(None)) -> dict:
    """认证中间件 - 从Header提取company_id

    用于需要认证的写操作端点 (POST/PUT/PATCH/DELETE)

    Raises:
        HTTPException: 未提供 company_id 时返回 401

    Returns:
        dict: 包含 company_id 的用户信息字典
    """
    if not x_company_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供 company_id，请通过 X-Company-ID Header 传递",
            headers={"WWW-Authenticate": "Company-ID"}
        )
    return {"company_id": x_company_id}


async def get_optional_user(x_company_id: Optional[str] = Header(None)) -> Optional[dict]:
    """可选认证 - 公共端点使用

    用于 GET 端点，允许不提供 company_id

    Returns:
        Optional[dict]: 如果提供了 company_id 则返回用户信息，否则返回 None
    """
    return {"company_id": x_company_id} if x_company_id else None