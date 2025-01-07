from tortoise import fields
from tortoise.exceptions import DoesNotExist
from fastapi import HTTPException

from app.models.base import BaseModel


class APP(BaseModel):
    """
    语言模型，提供语种的增删改查功能。
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, null=False, description="语种名称")
    abbrev = fields.CharField(max_length=50, null=False, description="语种简称")

    class Meta:
        table = "app"

    @classmethod
    async def get_detail(cls, lid: int):
        """
        获取语种详情。
        """
        try:
            language = await cls.get(id=lid, delete_time__isnull=True)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="没有找到相关语种")
        return language

    @classmethod
    async def get_all(cls):
        """
        获取所有语种。
        """
        languages = await cls.filter(delete_time__isnull=True).all()
        if not languages:
            raise HTTPException(status_code=404, detail="没有找到相关语种")
        return languages

    @classmethod
    async def new_language(cls, form: dict):
        """
        新增语种。
        """
        existing = await cls.filter(abbrev=form["abbrev"], delete_time__isnull=True).first()
        if existing:
            raise HTTPException(status_code=400, detail="语种已存在")

        await cls.create(
            name=form["name"],
            abbrev=form["abbrev"],
            create_by=form["username"],
            update_by=form["username"],
        )
        return {"msg": "语种创建成功"}

    @classmethod
    async def edit_language(cls, lid: int, form: dict):
        """
        编辑语种。
        """
        try:
            language = await cls.get(id=lid, delete_time__isnull=True)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="没有找到相关语种")

        await language.update(
            name=form["name"],
            abbrev=form["abbrev"],
            update_by=form["username"],
        )
        return {"msg": "语种更新成功"}

    @classmethod
    async def remove_language(cls, lid: int, form: dict):
        """
        软删除语种。
        """
        try:
            language = await cls.get(id=lid, delete_time__isnull=True)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="没有找到相关语种")

        await language.soft_delete(delete_by=form["username"])
        return {"msg": "语种已删除"}
