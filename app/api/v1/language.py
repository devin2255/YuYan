from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.language import CreateOrUpdateLanguage, DeleteLanguage
from app.services import language_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/languages")


@router.get("/{lid}")
def get_language(lid: str, db: Session = Depends(get_db)):
    data = language_service.get_language(db, int(lid))
    return success_response(data=to_dict(data))


@router.get("")
def get_languages(db: Session = Depends(get_db)):
    data = language_service.get_languages(db)
    return success_response(data=to_dict(data))


@router.post("")
async def create_language(payload: CreateOrUpdateLanguage, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    language_service.create_language(db, form)
    return success_response(msg="新建语种成功")


@router.put("/{language_id}")
async def update_language(language_id: str, payload: CreateOrUpdateLanguage, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    language_service.update_language(db, int(language_id), form)
    return success_response(msg="更新语种成功")


@router.delete("/{language_id}")
async def delete_language(language_id: str, payload: DeleteLanguage, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    language_service.delete_language(db, int(language_id), form)
    return success_response(msg="删除语种成功")
