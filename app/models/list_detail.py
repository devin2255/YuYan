import asyncio

from tortoise import fields
from app.models.base import BaseModel

class ListDetail(BaseModel):
    """
    名单详情模型类，继承自 BaseModel
    """
    id = fields.IntField(pk=True, description="自增主键")
    list_id = fields.ForeignKeyField('models.WordList', related_name='details', description="名单id，关联wordlist id字段")
    original_text = fields.CharField(max_length=100, null=False, description="原始文本内容")
    processed_text = fields.CharField(max_length=100, null=False, description="处理后的文本(如分词、去除特殊符号等)",
                                      index=True)
    memo = fields.CharField(max_length=100, null=True, description="备注")

    class Meta:
        table = "list_detail"  # 数据库表名

    @classmethod
    async def create_detail(cls, **kwargs):
        """
        创建新的名单详情
        :param kwargs: 详情字段
        :return: 创建的详情对象
        """
        return await cls.create(**kwargs)

    @classmethod
    async def get_details_by_list_id(cls, list_id: int):
        """
        根据名单ID获取详情列表
        :param list_id: 名单ID
        :return: 详情列表
        """
        return await cls.filter(list_id=list_id, delete_time__isnull=True).all()

    @classmethod
    async def get_details_by_list_id_pagination(
        cls, 
        list_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> dict:
        """
        根据名单ID分页获取详情列表
        :param list_id: 名单ID
        :param page: 当前页码，默认为1
        :param page_size: 每页数量，默认为10，最大100
        :return: 包含分页信息及数据的字典
        """
        # 确保分页参数有效
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)  # 限制每页最多100条
        
        offset = (page - 1) * page_size
        query = cls.filter(list_id=list_id, delete_time__isnull=True)

        # 并行获取总数和分页数据
        total, data = await asyncio.gather(
            query.count(),
            query.offset(offset).limit(page_size).all()
        )
        
        return {
            "items": data,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        }

    async def update_detail(self, **kwargs):
        """
        更新名单详情
        :param kwargs: 需要更新的字段
        :return: 更新后的详情对象
        """
        return await self.update(**kwargs)

    async def delete_detail(self):
        """
        删除名单详情
        :return: 删除结果
        """
        return await self.delete()