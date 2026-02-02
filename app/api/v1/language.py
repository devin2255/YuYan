from fastapi import APIRouter, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_db
from yuyan.app.schemas.language import CreateOrUpdateLanguage, DeleteLanguage
from yuyan.app.services import language_service
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/language")


@router.get("/{lid}")
def get_language(lid: str, db: Session = Depends(get_db)):
    data = language_service.get_language(db, int(lid))
    return success_response(data=to_dict(data))


@router.get("")
def get_languages(db: Session = Depends(get_db)):
    data = language_service.get_languages(db)
    return success_response(data=to_dict(data))


@router.post("")
async def create_language(request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = CreateOrUpdateLanguage(**payload)
    form = FormProxy(**form_data.dict())
    language_service.create_language(db, form)
    return success_response(msg="新建语种成功")


@router.put("/{language_id}")
async def update_language(language_id: str, request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = CreateOrUpdateLanguage(**payload)
    form = FormProxy(**form_data.dict())
    language_service.update_language(db, int(language_id), form)
    return success_response(msg="更新语种成功")


@router.delete("/{language_id}")
async def delete_language(language_id: str, request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = DeleteLanguage(**payload)
    form = FormProxy(**form_data.dict())
    language_service.delete_language(db, int(language_id), form)
    return success_response(msg="删除语种成功")
