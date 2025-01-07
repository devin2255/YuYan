import re
from datetime import datetime
from enum import Enum

from tortoise import fields, models
from tortoise.exceptions import DoesNotExist


class MixinJSONSerializer:
    """
    提供序列化支持的 Mixin 类。
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._fields = []
        self._include = []
        self._exclude = []
        self._set_fields()
        self._prune_fields()

    def _set_fields(self):
        pass

    def _prune_fields(self):
        columns = self.__annotations__.keys()
        if not self._fields:
            all_columns = set(columns)
            self._fields = list(all_columns - set(self._exclude))
            self._fields.extend(self._include)

    def hide(self, *args):
        for key in args:
            self._fields.remove(key)
        return self

    def keys(self):
        return self._fields

    def __getitem__(self, key):
        value = getattr(self, key)
        if isinstance(value, Enum):
            return value.name
        return value


class BaseModel(models.Model, MixinJSONSerializer):
    """
    提供软删除、创建时间、更新时间等基础功能的模型基类。
    """
    create_time = fields.DatetimeField(default=datetime.now)
    update_time = fields.DatetimeField(default=datetime.now)
    delete_time = fields.DatetimeField(null=True)
    create_by = fields.CharField(max_length=50, null=True)
    update_by = fields.CharField(max_length=50, null=True)
    delete_by = fields.CharField(max_length=50, null=True)

    class Meta:
        abstract = True

    def _set_fields(self):
        self._exclude = ["delete_time"]

    @property
    def _create_time(self):
        return int(round(self.create_time.timestamp() * 1000)) if self.create_time else None

    @property
    def _update_time(self):
        return int(round(self.update_time.timestamp() * 1000)) if self.update_time else None

    def soft_delete(self, delete_by: str = None):
        """
        软删除（标记 delete_time）。
        """
        self.delete_time = datetime.now()
        self.delete_by = delete_by
        return self.save()

    async def hard_delete(self):
        """
        硬删除（彻底删除）。
        """
        await self.delete()

    @classmethod
    async def get_or_404(cls, **kwargs):
        """
        根据条件获取单条记录，如果不存在则抛出 404 异常。
        """
        try:
            return await cls.get(**kwargs, delete_time__isnull=True)
        except DoesNotExist:
            raise Exception("Not Found")

    @classmethod
    async def first_or_404(cls, **kwargs):
        """
        根据条件获取第一条记录，如果不存在则抛出 404 异常。
        """
        instance = await cls.filter(**kwargs, delete_time__isnull=True).first()
        if not instance:
            raise Exception("Not Found")
        return instance

    @classmethod
    async def create(cls, **kwargs):
        """
        创建记录。
        """
        return await cls.create(**kwargs)

    async def update(self, **kwargs):
        """
        更新记录。
        """
        for key, value in kwargs.items():
            setattr(self, key, value)
        return await self.save()

    @classmethod
    async def query_all(cls, **kwargs):
        """
        查询所有记录（默认软删除过滤）。
        """
        return await cls.filter(**kwargs, delete_time__isnull=True)
