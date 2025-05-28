from fastapi import FastAPI

from app.models import load_models_from_folder
from app.config import settings
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware


def register_routers(app):
    from app.api.v1 import register_route_v1
    app.include_router(register_route_v1())


def register_db(app):
    model_modules = load_models_from_folder('./app/models')
    # 注册 Tortoise ORM 到 FastAPI
    register_tortoise(
        app,
        db_url=settings.database_url,
        modules={"models": model_modules},  # 动态加载所有模型模块
        generate_schemas=True,  # 自动生成数据库表
        add_exception_handlers=True,  # 添加异常处理器
    )


def apply_cors(app):
    # 配置跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 允许所有域名访问，或者指定具体的域名，如 ["https://example.com"]
        allow_credentials=True,  # 允许携带凭据（如 cookies）
        allow_methods=["*"],  # 允许所有 HTTP 方法，或者指定具体的方法，如 ["GET", "POST"]
        allow_headers=["*"],  # 允许所有请求头，或者指定具体的请求头
    )


def create_app(register_all=True):
    app = FastAPI(
        title=settings.app_name,
        docs_url="/docs",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css",
    )
    app.state.settings = settings  # 将 settings 挂载到 app.state

    if register_all:
        register_routers(app)
        register_db(app)

    return app

