from fastapi import APIRouter, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_db
from yuyan.app.schemas.risk_type import CreateRiskType
from yuyan.app.services import risk_type_service
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/risk_type")


@router.get("")
def get_risk_types(db: Session = Depends(get_db)):
    data = risk_type_service.get_risk_types(db)
    return success_response(data=to_dict(data))


@router.post("")
async def create_risk_type(request: Request, db: Session = Depends(get_db)):
    payload = await parse_request_payload(request)
    form_data = CreateRiskType(**payload)
    form = FormProxy(**form_data.dict())
    risk_type_service.create_risk_type(db, form)
    return success_response(msg="新建风险类型成功")
