from datetime import timedelta
import time
import uuid

import jwt
from passlib.context import CryptContext

from app.core.exceptions import ParameterException, Unauthorized
from app.models.user import User

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def _normalize_identity(identity: str) -> str:
    if identity is None:
        return ""
    return str(identity).strip().lower()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_user(db, identity: str, password: str, display_name: str) -> User:
    identity_norm = _normalize_identity(identity)
    if not identity_norm:
        raise ParameterException(message="账号不能为空")
    exist = db.query(User).filter(User.identity == identity_norm, User.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="账号已存在")
    user = User(
        identity=identity_norm,
        display_name=display_name or identity_norm,
        password_hash=hash_password(password),
        roles="admin",
        status=1,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db, identity: str, password: str) -> User:
    identity_norm = _normalize_identity(identity)
    user = db.query(User).filter(User.identity == identity_norm, User.delete_time.is_(None)).first()
    if not user:
        raise ParameterException(message="账号或密码错误")
    if user.status != 1:
        raise ParameterException(message="账号已禁用")
    if not verify_password(password, user.password_hash):
        raise ParameterException(message="账号或密码错误")
    return user


def _jwt_secret(ctx):
    return ctx.config.get("JWT_SECRET", "change-me")


def _jwt_algorithm(ctx):
    return ctx.config.get("JWT_ALGORITHM", "HS256")


def _encode(payload: dict, ctx) -> str:
    return jwt.encode(payload, _jwt_secret(ctx), algorithm=_jwt_algorithm(ctx))


def _decode(token: str, ctx) -> dict:
    try:
        return jwt.decode(token, _jwt_secret(ctx), algorithms=[_jwt_algorithm(ctx)])
    except jwt.ExpiredSignatureError:
        raise ParameterException(message="令牌已过期")
    except jwt.InvalidTokenError:
        raise ParameterException(message="令牌无效")


def create_access_token(ctx, user: User) -> str:
    ttl = int(ctx.config.get("JWT_ACCESS_TTL_MINUTES", 30))
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "identity": user.identity,
        "roles": user.role_list(),
        "type": "access",
        "iat": now,
        "exp": now + int(timedelta(minutes=ttl).total_seconds()),
    }
    return _encode(payload, ctx)


def create_refresh_token(ctx, user: User) -> str:
    ttl_days = int(ctx.config.get("JWT_REFRESH_TTL_DAYS", 30))
    now = int(time.time())
    jti = uuid.uuid4().hex
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "jti": jti,
        "iat": now,
        "exp": now + int(timedelta(days=ttl_days).total_seconds()),
    }
    token = _encode(payload, ctx)
    ttl_seconds = ttl_days * 86400
    ctx.redis.setex(_refresh_key(jti), ttl_seconds, str(user.id))
    return token


def rotate_refresh_token(ctx, db, refresh_token: str):
    payload = _decode(refresh_token, ctx)
    if payload.get("type") != "refresh":
        raise ParameterException(message="刷新令牌无效")
    jti = payload.get("jti")
    if not jti:
        raise ParameterException(message="刷新令牌无效")
    key = _refresh_key(jti)
    user_id = ctx.redis.get(key)
    if not user_id:
        raise ParameterException(message="刷新令牌已失效")
    ctx.redis.delete(key)
    user = db.query(User).filter(User.id == int(user_id), User.delete_time.is_(None)).first()
    if not user:
        raise ParameterException(message="账号不存在")
    new_token = create_refresh_token(ctx, user)
    return user, new_token


def revoke_refresh_token(ctx, refresh_token: str) -> None:
    payload = _decode(refresh_token, ctx)
    if payload.get("type") != "refresh":
        return
    jti = payload.get("jti")
    if not jti:
        return
    ctx.redis.delete(_refresh_key(jti))


def _refresh_key(jti: str) -> str:
    return f"refresh_token:{jti}"


def parse_access_token(ctx, token: str) -> dict:
    try:
        payload = _decode(token, ctx)
    except ParameterException as exc:
        raise Unauthorized(message=exc.message)
    if payload.get("type") != "access":
        raise Unauthorized(message="访问令牌无效")
    return payload


def build_user_payload(user: User) -> dict:
    return {
        "id": str(user.id),
        "displayName": user.display_name,
        "identity": user.identity,
        "roles": user.role_list(),
    }
