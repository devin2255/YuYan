from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.risk_type import CreateRiskType
from app.services import risk_type_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy

router = APIRouter(prefix="/risk-types", dependencies=[Depends(get_current_user)])


@router.get("")
def get_risk_types(db: Session = Depends(get_db)):
    data = risk_type_service.get_risk_types(db)
    return success_response(data=to_dict(data))


@router.post("")
async def create_risk_type(payload: CreateRiskType, db: Session = Depends(get_db)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    risk_type_service.create_risk_type(db, form)
    return success_response(msg="新建风险类型成功")
