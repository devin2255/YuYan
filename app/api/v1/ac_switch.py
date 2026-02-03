from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db
from app.schemas.switch import CreateACSwitch, UpdateACSwitch
from app.services import app_service, switch_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/ac-switches")


@router.get("/{id}")
def get_ac_switch(id: str, db: Session = Depends(get_db)):
    data = switch_service.get_ac_switch(db, int(id))
    return to_dict(data)


@router.get("")
def get_ac_switchs(db: Session = Depends(get_db)):
    data = switch_service.get_ac_switchs(db)
    return to_dict(data)


@router.post("")
async def create_ac_switch(payload: CreateACSwitch, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    app_service.get_app(db, form.app_id.data)
    switch_service.create_ac_switch(db, ctx, form)
    return success_response(msg="新建成功")


@router.put("/{id}")
async def update_ac_switch(id: str, payload: UpdateACSwitch, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    switch_service.update_ac_switch(db, ctx, int(id), form)
    return success_response(msg="更新成功")


@router.delete("/{id}")
def delete_ac_switch(id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    switch_service.delete_ac_switch(db, ctx, int(id))
    return success_response(msg="删除成功")
