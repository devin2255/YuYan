from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_ctx, get_db
from yuyan.app.schemas.switch import CreateThreshold, UpdateThreshold
from yuyan.app.services import game_service, switch_service
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/model_threshold")


@router.get("/{id}")
def get_threshold(id: str, db: Session = Depends(get_db)):
    data = switch_service.get_threshold(db, int(id))
    return to_dict(data)


@router.get("")
def get_thresholds(db: Session = Depends(get_db)):
    data = switch_service.get_thresholds(db)
    return to_dict(data)


@router.post("")
async def create_threshold(request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = CreateThreshold(**payload)
    form = FormProxy(**form_data.dict())
    game_service.get_game(db, form.game_id.data)
    switch_service.create_threshold(db, ctx, form)
    return success_response(msg="新建成功")


@router.put("/{id}")
async def update_threshold(id: str, request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = UpdateThreshold(**payload)
    form = FormProxy(**form_data.dict())
    switch_service.update_threshold(db, ctx, int(id), form)
    return success_response(msg="更新成功")


@router.delete("/{id}")
def delete_threshold(id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    switch_service.delete_threshold(db, ctx, int(id))
    return success_response(msg="删除成功")
