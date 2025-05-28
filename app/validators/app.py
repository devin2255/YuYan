from typing import Optional

from pydantic import BaseModel, Field


class CreateAppRequest(BaseModel):
    """
    创建应用的请求体模型。
    """
    app_name: str = Field(..., min_length=1, max_length=50, description="应用名称，非空且最多50个字符")
    app_id: str = Field(..., min_length=1, max_length=10, description="应用ID，非空且最多10个字符")
    username: Optional[str] = Field(None, max_length=10, description='用户名')


class UpdateAppRequest(BaseModel):
    """
    创建应用的请求体模型。
    """
    app_name: str = Field(..., min_length=1, max_length=50, description="应用名称，非空且最多50个字符")
    # app_id: str = Field(..., max_length=10, description="应用ID，非空且最多10个字符")
    username: Optional[str] = Field(None, max_length=10, description='用户名')
