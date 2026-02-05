from __future__ import annotations

from fastapi import Depends, Request

from app.core.exceptions import Unauthorized
from app.models.user import User
from app.services import auth_service


def get_ctx(request: Request):
    return request.app.state.ctx


def get_db(request: Request):
    db = request.app.state.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    db=Depends(get_db),
    ctx=Depends(get_ctx),
):
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise Unauthorized(message="访问令牌缺失")
    token = auth.replace("Bearer ", "", 1).strip()
    payload = auth_service.parse_access_token(ctx, token)
    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized(message="访问令牌无效")
    user = db.query(User).filter(User.id == int(user_id), User.delete_time.is_(None)).first()
    if not user or user.status != 1:
        raise Unauthorized(message="账号不存在或已禁用")
    return user
