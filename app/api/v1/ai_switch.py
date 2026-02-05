from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db, get_current_user
from app.schemas.switch import CreateAISwitch, UpdateAISwitch
from app.services import app_service, switch_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/ai-switches", dependencies=[Depends(get_current_user)])


@router.get("/{id}")
def get_ai_switch(id: str, db: Session = Depends(get_db)):
    data = switch_service.get_ai_switch(db, int(id))
    return to_dict(data)


@router.get("")
def get_ai_switchs(db: Session = Depends(get_db)):
    data = switch_service.get_ai_switchs(db)
    return to_dict(data)


@router.post("")
async def create_ai_switch(payload: CreateAISwitch, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    app_service.get_app(db, form.app_id.data)
    switch_service.create_ai_switch(db, ctx, form)
    return success_response(msg="新建成功")


@router.put("/{id}")
async def update_ai_switch(id: str, payload: UpdateAISwitch, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    switch_service.update_ai_switch(db, ctx, int(id), form)
    return success_response(msg="更新成功")


@router.delete("/{id}")
def delete_ai_switch(id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    switch_service.delete_ai_switch(db, ctx, int(id))
    return success_response(msg="删除成功")
