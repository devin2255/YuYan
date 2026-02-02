from sqlalchemy import Boolean, Column, Integer, String

from yuyan.app.models.base import BaseModel
from yuyan.app.utils.enums import (
    ListMatchRuleEnum,
    ListMatchTypeEnum,
    ListRiskTypeEnum,
    ListStatusEnum,
    ListSuggestEnum,
    ListTypeEnum,
)


class NameList(BaseModel):
    id = Column(Integer, primary_key=True, autoincrement=True)
    no = Column(String(100), unique=True, index=True)
    name = Column(String(100), nullable=False)
    _type = Column("type", Integer)
    _match_rule = Column("match_rule", Integer)
    _match_type = Column("match_type", Integer, default=1)
    _suggest = Column("suggest", Integer)
    _risk_type = Column("risk_type", Integer)
    _status = Column("status", Boolean(), default=1)
    language = Column(String(50))

    @property
    def type(self):
        return ListTypeEnum(self._type)

    @property
    def match_rule(self):
        return ListMatchRuleEnum(self._match_rule)

    @property
    def match_type(self):
        return ListMatchTypeEnum(self._match_type)

    @property
    def suggest(self):
        return ListSuggestEnum(self._suggest)

    @property
    def risk_type(self):
        return ListRiskTypeEnum(self._risk_type)

    @property
    def status(self):
        return ListStatusEnum(self._status)

    def to_dict(self):
        data = super().to_dict()
        data["type"] = self._type
        data["match_rule"] = self._match_rule
        data["match_type"] = self._match_type
        data["suggest"] = self._suggest
        data["risk_type"] = self._risk_type
        data["status"] = int(self._status)
        data.pop("_type", None)
        data.pop("_match_rule", None)
        data.pop("_match_type", None)
        data.pop("_suggest", None)
        data.pop("_risk_type", None)
        data.pop("_status", None)
        return data
