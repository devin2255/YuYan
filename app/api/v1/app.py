from tortoise.exceptions import DoesNotExist

from app.api import BluePrint
from app.models.app import App
from app.validators.app import CreateAppRequest
from app.config.constants import ERROR_MESSAGES
from fastapi import HTTPException, status

app_api = BluePrint('app')


@app_api.route('', methods=["GET"])
async def get_apps():
    apps = await App.get_all_apps()
    return apps


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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.APP_EXISTS)

        # 创建应用记录
        create_data = {
            "app_name": request.app_name,
            "app_id": request.app_id
        }
        if request.username is not None:
            create_data["username"] = request.username
        app = await App.create(**create_data)
        return app
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


