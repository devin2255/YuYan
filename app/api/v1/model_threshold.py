from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db
from app.schemas.switch import CreateThreshold, UpdateThreshold
from app.services import app_service, switch_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/model-thresholds")


@router.get("/{id}")
def get_threshold(id: str, db: Session = Depends(get_db)):
    data = switch_service.get_threshold(db, int(id))
    return to_dict(data)


@router.get("")
def get_thresholds(db: Session = Depends(get_db)):
    data = switch_service.get_thresholds(db)
    return to_dict(data)


@router.post("")
async def create_threshold(payload: CreateThreshold, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    app_service.get_app(db, form.app_id.data)
    switch_service.create_threshold(db, ctx, form)
    return success_response(msg="新建成功")


@router.put("/{id}")
async def update_threshold(id: str, payload: UpdateThreshold, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    switch_service.update_threshold(db, ctx, int(id), form)
    return success_response(msg="更新成功")


@router.delete("/{id}")
def delete_threshold(id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    switch_service.delete_threshold(db, ctx, int(id))
    return success_response(msg="删除成功")
