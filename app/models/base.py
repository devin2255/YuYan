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
        self._fields = []  # 最终需要序列化的字段列表
        self._include = []  # 需要额外包含的字段
        self._exclude = []  # 需要排除的字段
        self._set_fields()  # 初始化字段
        self._prune_fields()  # 过滤字段

    def _set_fields(self):
        """
        初始化字段配置。
        子类可以重写此方法以自定义字段。
        """
        pass

    def _prune_fields(self):
        """
        根据 _fields、_include 和 _exclude 动态生成最终的字段列表。
        """
        # 获取所有字段（包括 Tortoise ORM 的字段）
        columns = [field for field in self._meta.fields_map.keys()]

        if not self._fields:
            all_columns = set(columns)
            self._fields = list(all_columns - set(self._exclude))  # 排除 _exclude 中的字段
            self._fields.extend(self._include)  # 添加 _include 中的字段

    def hide(self, *args):
        """
        动态隐藏某些字段。
        """
        for key in args:
            self._fields.remove(key)  # 从 _fields 中移除指定的字段
        return self

    def keys(self):
        """
        返回需要序列化的字段列表。
        """
        return self._fields

    def __getitem__(self, key):
        """
        获取字段的值，支持对 Enum 类型的字段进行特殊处理。
        """
        value = getattr(self, key)
        if isinstance(value, Enum):
            return value.name  # 如果是枚举类型，返回枚举值的名称
        return value


class BaseModel(models.Model):
    """
    提供软删除、创建时间、更新时间等基础功能的模型基类。
    """
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")
    delete_time = fields.DatetimeField(null=True, description="删除时间")
    create_by = fields.CharField(max_length=50, null=True, description="创建人")
    update_by = fields.CharField(max_length=50, null=True, description="更新人")
    delete_by = fields.CharField(max_length=50, null=True, description="删除人")

    class Meta:
        abstract = True  # 抽象类，不会创建数据库表

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 自动设置表名
        if not hasattr(self.Meta, "table"):
            self.Meta.table = camel2line(self.__class__.__name__)

    def _set_fields(self):
        self._exclude = ["delete_time"]

    @property
    def _create_time(self):
        if self.create_time is None:
            return None
        return int(round(self.create_time.timestamp() * 1000))

    @property
    def _update_time(self):
        if self.update_time is None:
            return None
        return int(round(self.update_time.timestamp() * 1000))

    def set_attrs(self, attrs_dict: dict):
        """
        批量设置属性
        """
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)

    async def delete(self, delete_by: str = None):
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
        return await super().delete()

    @classmethod
    async def get(cls, **kwargs):
        """
        查询单条记录
        """
        if "delete_time" not in kwargs:
            kwargs["delete_time"] = None  # 默认过滤已删除的记录
        return await cls.filter(**kwargs).first()

    @classmethod
    async def create(cls, **kwargs):
        """
        创建记录
        """
        obj = cls()
        obj.set_attrs(kwargs)
        await obj.save()
        return obj

    async def update(self, **kwargs):
        """
        更新记录
        """
        self.set_attrs(kwargs)
        await self.save()
        return self

    @classmethod
    async def query_all(cls, **kwargs):
        """
        查询所有记录（默认软删除过滤）。
        """
        return await cls.filter(**kwargs, delete_time__isnull=True).all()


def camel2line(camel: str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    line = re.sub(p, r'\1_\2', camel).lower()
    return line

