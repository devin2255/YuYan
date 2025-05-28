from fastapi import status, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from app.config.constants import ERROR_MESSAGES
from app.libs.enums import LanguageEnum, ListSuggestEnum, ListTypeEnum, MatchRuleEnum, RiskTypeEnum, SwitchEnum


class CreateOrUpdateWordListRequest(BaseModel):
    """
    创建名单的请求体模型。
    """
    list_name: str = Field(..., max_length=100, description="名单名称")
    list_type: int = Field(..., description="名单类型")
    match_rule: int = Field(..., description="匹配规则")
    suggestion: int = Field(..., description="处置建议")
    risk_type: int = Field(..., description="风险类型")
    status: int = Field(default=SwitchEnum.ON.value, description="名单状态")
    language: int = Field(default=LanguageEnum.ALL.value, description="名单语种")
    username: str = Field(None, max_length=10, description='用户名')

    @model_validator(mode='after')
    def validate_all_fields(self):
        if self.list_type not in ListTypeEnum.values():
            # raise ValueError(f"无效的名单类型，可选值为: {ListTypeEnum.values()}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_LIST_TYPE
            )
        if self.match_rule not in MatchRuleEnum.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_LIST_MATCH_RULE
            )
        if self.suggestion not in ListSuggestEnum.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_LIST_SUGGESTION
            )
        if self.risk_type not in RiskTypeEnum.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_RISK_TYPE
            )
        if self.status not in SwitchEnum.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_STATUS
            )
        if self.language not in LanguageEnum.values():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES.INVALID_LANGUAGE
            )
        return self

    # @field_validator('list_type')
    # def validate_list_type(cls, v):
    #     if v not in ListTypeEnum.values():
    #         raise ValueError(f"无效的名单类型，可选值为: {ListTypeEnum.values()}")
    #     return v
    #
    # @field_validator('match_rule')
    # def validate_match_rule(cls, v):
    #     if v not in MatchRuleEnum.values():
    #         raise ValueError(f"无效的匹配规则，可选值为: {MatchRuleEnum.values()}")
    #     return v
    #
    # @field_validator('suggestion')
    # def validate_suggestion(cls, v):
    #     if v not in ListSuggestEnum.values():
    #         raise ValueError(f"无效的处置建议，可选值为: {ListSuggestEnum.values()}")
    #     return v
    #
    # @field_validator('risk_type')
    # def validate_risk_type(cls, v):
    #     if v not in RiskTypeEnum.values():
    #         raise ValueError(f"无效的风险类型，可选值为: {RiskTypeEnum.values()}")
    #     return v
    #
    # @field_validator('status')
    # def validate_status(cls, v):
    #     if v not in SwitchEnum.values():
    #         raise ValueError(f"无效的名单状态，可选值为: {SwitchEnum.values()}")
    #     return v
    #
    # @field_validator('language')
    # def validate_language(cls, v):
    #     if v not in LanguageEnum.values():
    #         raise ValueError(f"无效的名单语种，可选值为: {LanguageEnum.values()}")
    #     return v


# class UpdateWordListRequest(BaseModel):
#     """
#     更新名单的请求体模型。
#     """
#     list_name: str = Field(None, max_length=100, description="名单名称")
#     list_type: int = Field(None, description="名单类型")
#     match_rule: int = Field(None, description="匹配规则")
#     suggestion: int = Field(None, description="处置建议")
#     risk_type: int = Field(None, description="风险类型")
#     status: int = Field(None, description="名单状态")
#     language: int = Field(None, description="名单语种")
#
#     @field_validator('list_type')
#     def validate_list_type(cls, v):
#         if v is not None and v not in ListTypeEnum.values():
#             raise ValueError(f"无效的名单类型，可选值为: {ListTypeEnum.values()}")
#         return v
#
#     @field_validator('match_rule')
#     def validate_match_rule(cls, v):
#         if v is not None and v not in MatchRuleEnum.values():
#             raise ValueError(f"无效的匹配规则，可选值为: {MatchRuleEnum.values()}")
#         return v
#
#     @field_validator('suggestion')
#     def validate_suggestion(cls, v):
#         if v is not None and v not in ListSuggestEnum.values():
#             raise ValueError(f"无效的处置建议，可选值为: {ListSuggestEnum.values()}")
#         return v
#
#     @field_validator('risk_type')
#     def validate_risk_type(cls, v):
#         if v is not None and v not in RiskTypeEnum.values():
#             raise ValueError(f"无效的风险类型，可选值为: {RiskTypeEnum.values()}")
#         return v
#
#     @field_validator('status')
#     def validate_status(cls, v):
#         if v is not None and v not in SwitchEnum.values():
#             raise ValueError(f"无效的名单状态，可选值为: {SwitchEnum.values()}")
#         return v
#
#     @field_validator('language')
#     def validate_language(cls, v):
#         if v is not None and v not in LanguageEnum.values():
#             raise ValueError(f"无效的名单语种，可选值为: {LanguageEnum.values()}")
#         return v