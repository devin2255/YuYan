from __future__ import annotations

import json
import sys
import time
import traceback
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

# Allow running via "uvicorn app.main:app" from the repo root.
_repo_parent = Path(__file__).resolve().parents[2]
if _repo_parent.is_dir() and str(_repo_parent) not in sys.path:
    sys.path.insert(0, str(_repo_parent))

import redis
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import router as v1_router
from app.core.config import load_settings
from app.core.context import AppContext
from app.core.db import Base, init_engine
from app.core.exceptions import APIException, ServerError
from app.core.logging import KafkaLog, setup_logging
from app.core.scheduler import create_scheduler
from app.services.cache import load_cache_from_redis, load_chat_sentinel
from app.utils.send_feishu import send_feishu_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = load_settings()
    settings_dict = settings.as_dict()
    logger = setup_logging(settings_dict.get("LOG", {}))

    # 资源初始化
    redis_url = settings_dict.get("REDIS_URL")
    chat_redis_url = settings_dict.get("CHAT_LOG_REDIS_URL") or redis_url
    redis_client = redis.Redis.from_url(redis_url, decode_responses=True)
    chat_redis_client = redis.Redis.from_url(chat_redis_url, decode_responses=True)
    kafka_logger = KafkaLog(settings_dict.get("KAFKA_LOG_DIR", "logs/kafka"))
    engine, SessionLocal = init_engine(settings_dict.get("SQLALCHEMY_DATABASE_URI"))
    # ensure models are registered
    from app import models  # noqa: F401
    auto_create = settings_dict.get("AUTO_CREATE_TABLES")
    if auto_create is None:
        env = str(settings_dict.get("ENVIRONMENT", "")).lower()
        auto_create = env != "production"
    if auto_create:
        Base.metadata.create_all(bind=engine)

    ctx = AppContext(
        settings=settings,
        logger=logger,
        redis=redis_client,
        chat_redis=chat_redis_client,
        kafka_logger=kafka_logger,
        config=settings_dict,
    )
    ctx.config["REQUESTS_SESSION"] = requests.Session()
    ctx.config["REDIS_CLIENT"] = redis_client
    ctx.config["CHAT_LOG_REDIS_CLIENT"] = chat_redis_client
    ctx.config["kafka_logger"] = kafka_logger

    # 读取黑名单 IP
    ip_file = Path(ctx.config.get("BLACK_CLIENT_IP_FILE", "app/config/black_client_ip.txt"))
    if ip_file.exists():
        ctx.config["BLACK_CLIENT_IP"] = [i.strip() for i in ip_file.read_text(encoding="utf-8").splitlines() if i]
    else:
        ctx.config["BLACK_CLIENT_IP"] = []

    # 初始化本地缓存
    all_apps, app_channel, cache_data, access_key = load_cache_from_redis(redis_client)
    ctx.config["ALL_APPS"] = all_apps
    ctx.config["APP_CHANNEL"] = app_channel
    ctx.config["CACHE_DATA"] = cache_data
    ctx.config["ACCESS_KEY"] = access_key
    ctx.config["CHAT_SENTINEL"] = load_chat_sentinel(redis_client)

    app.state.ctx = ctx
    app.state.SessionLocal = SessionLocal
    app.state.engine = engine

    scheduler = create_scheduler(ctx)
    app.state.scheduler = scheduler
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown()
        try:
            ctx.config["REQUESTS_SESSION"].close()
        except Exception:
            pass
        engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_log_middleware(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        ctx = request.app.state.ctx
        log_config = ctx.config.get("LOG", {})
        if log_config.get("REQUEST_LOG"):
            request_ip = request.headers.get("Yz-Client-Ip")
            if request_ip:
                request_ip = request_ip.split(",")[0]
            else:
                request_ip = request.client.host if request.client else ""
            message = "[%s] -> [%s] from:%s content-type:%s costs:%.3f ms" % (
                request.method,
                request.url.path,
                request_ip,
                request.headers.get("content-type"),
                (time.time() - start) * 1000,
            )
            if log_config.get("LEVEL") == "INFO":
                ctx.logger.info(message)
            else:
                ctx.logger.debug(message)
        return response

    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException):
        payload = {"message": exc.message, "code": exc.error_code, "requestId": exc.request_id}
        if exc.data:
            payload["data"] = exc.data
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        ctx = request.app.state.ctx
        if "v1" in request.url.path or "dun" in request.url.path:
            try:
                body = await request.body()
                try:
                    data = json.loads(body.decode("utf-8")) if body else {}
                except Exception:
                    data = body.decode("utf-8", errors="ignore") if body else ""
                error_info = {
                    "url": str(request.url),
                    "method": request.method,
                    "headers": dict(request.headers),
                    "body": data,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "stack_trace": traceback.format_exc(),
                }
                send_feishu_message(error_info)
            except Exception as err:
                ctx.logger.debug(f"send feishu error: {err}")

        request_id = str(uuid.uuid1())
        payload = {
            "message": ServerError.message,
            "code": ServerError.error_code,
            "requestId": request_id,
        }
        return JSONResponse(status_code=500, content=payload)

    app.include_router(v1_router)
    return app


app = create_app()
