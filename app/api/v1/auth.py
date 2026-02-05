from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.api.deps import get_ctx, get_db
from app.core.exceptions import ParameterException, Unauthorized
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services import auth_service
from app.models.user import User
from app.services.response import success_response

router = APIRouter(prefix="/auth")


def _set_refresh_cookie(response: JSONResponse, token: str, ctx) -> None:
    cookie_name = ctx.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    max_age = int(ctx.config.get("JWT_REFRESH_TTL_DAYS", 30)) * 86400
    secure = bool(ctx.config.get("JWT_COOKIE_SECURE", False))
    samesite = ctx.config.get("JWT_COOKIE_SAMESITE", "lax")
    response.set_cookie(
        key=cookie_name,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=secure,
        samesite=samesite,
        path="/",
    )


def _clear_refresh_cookie(response: JSONResponse, ctx) -> None:
    cookie_name = ctx.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    response.delete_cookie(key=cookie_name, path="/")


def _get_refresh_cookie(request: Request, ctx) -> str:
    cookie_name = ctx.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token")
    token = request.cookies.get(cookie_name)
    if not token:
        raise ParameterException(message="刷新令牌缺失")
    return token


def _get_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization") or ""
    if not auth.startswith("Bearer "):
        raise Unauthorized(message="访问令牌缺失")
    return auth.replace("Bearer ", "", 1).strip()


@router.post("/login")
def login(payload: LoginRequest, db=Depends(get_db), ctx=Depends(get_ctx)):
    user = auth_service.authenticate_user(db, payload.identity, payload.password)
    access_token = auth_service.create_access_token(ctx, user)
    refresh_token = auth_service.create_refresh_token(ctx, user)
    response = JSONResponse(
        content=success_response(
            data={
                "access_token": access_token,
                "user": auth_service.build_user_payload(user),
            }
        )
    )
    _set_refresh_cookie(response, refresh_token, ctx)
    return response


@router.post("/register")
def register(payload: RegisterRequest, db=Depends(get_db), ctx=Depends(get_ctx)):
    user = auth_service.create_user(db, payload.identity, payload.password, payload.display_name)
    access_token = auth_service.create_access_token(ctx, user)
    refresh_token = auth_service.create_refresh_token(ctx, user)
    response = JSONResponse(
        content=success_response(
            data={
                "access_token": access_token,
                "user": auth_service.build_user_payload(user),
            }
        )
    )
    _set_refresh_cookie(response, refresh_token, ctx)
    return response


@router.post("/refresh")
def refresh_token(request: Request, db=Depends(get_db), ctx=Depends(get_ctx)):
    refresh_token = _get_refresh_cookie(request, ctx)
    user, new_refresh = auth_service.rotate_refresh_token(ctx, db, refresh_token)
    access_token = auth_service.create_access_token(ctx, user)
    response = JSONResponse(
        content=success_response(
            data={
                "access_token": access_token,
                "user": auth_service.build_user_payload(user),
            }
        )
    )
    _set_refresh_cookie(response, new_refresh, ctx)
    return response


@router.get("/me")
def me(request: Request, db=Depends(get_db), ctx=Depends(get_ctx)):
    token = _get_bearer_token(request)
    payload = auth_service.parse_access_token(ctx, token)
    user_id = payload.get("sub")
    if not user_id:
        raise Unauthorized(message="访问令牌无效")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise Unauthorized(message="账号不存在")
    return success_response(data=auth_service.build_user_payload(user))


@router.post("/logout")
def logout(request: Request, ctx=Depends(get_ctx)):
    token = request.cookies.get(ctx.config.get("JWT_REFRESH_COOKIE_NAME", "refresh_token"))
    if token:
        try:
            auth_service.revoke_refresh_token(ctx, token)
        except Exception:
            pass
    response = JSONResponse(content=success_response(msg="退出成功"))
    _clear_refresh_cookie(response, ctx)
    return response
