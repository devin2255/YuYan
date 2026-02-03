import time

from sqlalchemy.orm import Session

from app.core.exceptions import NotFound, ParameterException
from app.models.app import App
from app.utils.md5_util import generate_md5


def get_app(db: Session, app_id: str):
    app = db.query(App).filter(App.app_id == app_id, App.delete_time.is_(None)).first()
    if not app:
        raise NotFound(message="没有找到相关应用")
    return app


def get_apps(db: Session):
    apps = db.query(App).filter(App.delete_time.is_(None)).all()
    if not apps:
        raise NotFound(message="没有找到相关应用")
    return apps


def create_app(db: Session, ctx, form):
    app = db.query(App).filter(App.app_id == form.app_id.data, App.delete_time.is_(None)).first()
    if app:
        raise ParameterException(message="应用已存在")

    access_key = generate_md5(str(form.app_id.data) + str(int(time.time() * 1000)))
    new_app = App(
        app_id=form.app_id.data,
        name=form.name.data,
        access_key=access_key,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(new_app)
    db.commit()

    redis_client = ctx.config["REDIS_CLIENT"]
    redis_client.sadd("all_apps", form.app_id.data)
    redis_client.hset("access_key", form.app_id.data, access_key)
    ctx.config.setdefault("ALL_APPS", []).append(form.app_id.data)
    ctx.config.setdefault("ACCESS_KEY", {})[form.app_id.data] = access_key
    return access_key


def update_app(db: Session, ctx, app_id: str, form):
    app = get_app(db, app_id)
    app.name = form.name.data
    app.update_by = form.username.data
    db.add(app)
    db.commit()

    return True


def delete_app(db: Session, ctx, app_id: str):
    app = get_app(db, app_id)
    app.soft_delete()
    db.add(app)
    db.commit()

    redis_client = ctx.config["REDIS_CLIENT"]
    redis_client.srem("all_apps", app_id)
    redis_client.hdel("access_key", app_id)
    ctx.config.setdefault("ALL_APPS", [])
    if app_id in ctx.config["ALL_APPS"]:
        ctx.config["ALL_APPS"].remove(app_id)
    if ctx.config.get("ACCESS_KEY"):
        ctx.config["ACCESS_KEY"].pop(app_id, None)
    return True
