from tortoise.exceptions import DoesNotExist

from app.api import BluePrint
from app.models.app import App
from pydantic import BaseModel, Field, ValidationError
from fastapi import HTTPException

app_api = BluePrint('app')


@app_api.route('', methods=["GET"])
async def get_apps():
    apps = await App.get_all_apps()
    return apps


class CreateAppRequest(BaseModel):
    """
    创建应用的请求体模型。
    """
    app_name: str = Field(..., max_length=50, description="应用名称，最多50个字符")
    app_id: str = Field(..., max_length=10, description="应用ID，最多10个字符")


@app_api.route('', methods=["POST"])
async def create_app(request: CreateAppRequest):
    """
        创建新应用。

        :param request: 包含应用名称和 app_id 的请求体
        :return: 创建的应用记录
        """
    try:
        # 检查 app_id 是否已存在
        existing_app = await App.get_by_app_id(request.app_id)
        if existing_app:
            raise HTTPException(status_code=400, detail="app_id 已存在")
    except DoesNotExist:
        pass  # app_id 不存在，可以继续创建

    try:
        # 创建应用记录
        app = await App.create(app_name=request.app_name, app_id=request.app_id)
        return app
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


