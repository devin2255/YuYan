from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db
from app.schemas.app import CreateApp, UpdateApp
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy
from app.services import app_service

router = APIRouter(prefix="/apps")


@router.get("/{app_id}")
def get_app(app_id: str, db: Session = Depends(get_db)):
    app = app_service.get_app(db, app_id)
    return success_response(data=to_dict(app))


@router.get("")
def get_apps(db: Session = Depends(get_db)):
    apps = app_service.get_apps(db)
    return success_response(data=to_dict(apps))


@router.post("")
async def create_app(payload: CreateApp, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form = FormProxy(**payload.model_dump())
    access_key = app_service.create_app(db, ctx, form)
    return success_response(msg=f"新建应用成功, access_key: {access_key}")


@router.put("/{app_id}")
async def update_app(app_id: str, payload: UpdateApp, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form = FormProxy(**payload.model_dump())
    app_service.update_app(db, ctx, app_id, form)
    return success_response(msg="更新应用成功")


@router.delete("/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    app_service.delete_app(db, ctx, app_id)
    return success_response(msg="删除应用成功")
