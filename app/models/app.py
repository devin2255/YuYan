import hashlib
from datetime import datetime
from tortoise import fields
from app.models.base import BaseModel
from fastapi import HTTPException, status
from app.config.constants import ERROR_MESSAGES


class App(BaseModel):
    """
    应用模型类，继承自 BaseModel。
    """
    id = fields.IntField(pk=True, description="自增主键")
    app_name = fields.CharField(max_length=100, description="应用名称")
    app_id = fields.CharField(max_length=50, unique=True, description="应用唯一标识")
    app_key = fields.CharField(max_length=100, unique=True, description="用于身份校验的key")

    class Meta:
        table = "app"  # 数据库表名

    def _set_fields(self):
        """
        初始化字段配置。
        """
        self._exclude = ["delete_time", "app_key"]  # 默认隐藏 app_key 字段

    @classmethod
    async def create(cls, **kwargs):
        """
        创建应用记录，并自动生成 app_key。
        """
        app_id = kwargs.get("app_id")
        # if not app_id:
        #     raise ValueError("app_id 不能为空")

        # 生成 app_key
        app_key = cls.generate_app_key(app_id)

        # 创建记录
        kwargs["app_key"] = app_key
        return await super().create(**kwargs)

    @staticmethod
    def generate_app_key(app_id: str, key_length: int = 64) -> str:
        """
        根据 app_id 和当前时间生成一个固定长度且不可逆的 app_key。

        :param app_id: 应用唯一标识
        :param key_length: 生成的 app_key 的长度，默认为 32
        :return: 固定长度且不可逆的 app_key
        """
        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # 拼接 app_id 和时间戳
        raw_string = f"{app_id}_{timestamp}"

        # 使用 SHA-256 哈希算法生成哈希值
        hash_object = hashlib.sha256(raw_string.encode())
        hash_hex = hash_object.hexdigest()

        # 截取前 key_length 位作为 app_key
        return hash_hex[:key_length]

    async def update(self, app_id: int, **kwargs):
        """
        更新应用记录。
        """
        app = await self.get(id=app_id)
        # if "app_id" in kwargs:
        #     raise ValueError("app_id 不可更新")
        if "app_key" in kwargs:
            # raise ValueError("app_key 不可更新")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_MESSAGES.APP_KEY_NOT_SUPPORT_UPDATES)
        return await app.update(**kwargs)

    @classmethod
    async def get_by_app_id(cls, app_id: str):
        """
        根据 app_id 查询应用记录。
        """
        return await cls.get(app_id=app_id)

    @classmethod
    async def get_all_apps(cls):
        """
        查询所有应用记录（默认软删除过滤）。
        """
        return await cls.query_all()

    async def soft_delete_by_id(self, app_id: int, delete_by: str = None):
        """
        根据 id 主键软删除应用记录。

        :param app_id: 应用的主键 id
        :param delete_by: 删除操作执行人
        :return: 删除是否成功
        """
        app = await self.get(id=app_id)
        return await app.delete(delete_by=delete_by)

    async def hard_delete_by_id(self, app_id: int):
        """
        根据 id 主键硬删除应用记录。

        :param app_id: 应用的主键 id
        :return: 删除是否成功
        """
        app = await self.get(id=app_id)
        return await app.hard_delete()
