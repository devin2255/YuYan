from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.risk_type import RiskType


def get_risk_types(db: Session):
    items = db.query(RiskType).filter(RiskType.delete_time.is_(None)).all()
    if not items:
        raise NotFound(message="没有找到相关风险类型")
    return items


def create_risk_type(db: Session, form):
    exist = db.query(RiskType).filter(RiskType.no == form.no.data, RiskType.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="风险类型已存在")
    risk_type = RiskType(
        no=form.no.data,
        abbrev=form.abbrev.data,
        desc=form.desc.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(risk_type)
    db.commit()
    return True
