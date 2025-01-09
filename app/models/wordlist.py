
import hashlib
from datetime import datetime
from tortoise import fields

from app.libs.enums import ListTypeEnum, MatchRuleEnum, ListSuggestEnum, RiskTypeEnum, SwitchEnum, LanguageEnum
from app.models.base import BaseModel


class WordList(BaseModel):
    """
    名单模型类，继承自 BaseModel。
    """
    id = fields.IntField(pk=True, description="自增主键")
    list_name = fields.CharField(max_length=100, description="名单名称")
    list_type = fields.IntEnumField(ListTypeEnum, max_length=50, description="名单类型")
    match_rule = fields.IntEnumField(MatchRuleEnum, description="匹配规则: 0-文本加昵称 | 1-文本 | 2-昵称 | 3-IP | 4-accountId | 5-role_id")
    suggestion = fields.IntEnumField(ListSuggestEnum, description="处置建议: 0: PASS | 1: REJECT | 2: REVIEW")
    risk_type = fields.IntEnumField(RiskTypeEnum, description="风险类型: 0-正常 | 100-涉政 | 200-色情 | 300-辱骂 | 400-广告 | 500-无意义 | 600-违禁 | 700-其他 | 800-黑账号 | 900-黑IP | 810-高危账号 | 910-高危IP | 1000-自定义")
    status = fields.IntEnumField(SwitchEnum, default=SwitchEnum.ON.value, description="名单状态: 1-启用 | 0-停用")
    language = fields.IntEnumField(LanguageEnum, default=LanguageEnum.ALL.value, description="名单语种，默认为全部语种")

    class Meta:
        table = "wordlist"  # 数据库表名

    @classmethod
    async def create_wordlist(cls, **kwargs):
        """
        创建新的名单
        :param kwargs: 名单字段
        :return: 创建的名单对象
        """
        return await super().create(**kwargs)

    @classmethod
    async def get_wordlist_by_id(cls, wordlist_id: int):
        """
        根据ID获取名单
        :param wordlist_id: 名单ID
        :return: 名单对象
        """
        return await cls.get(id=wordlist_id)

    @classmethod
    async def get_wordlist_by_name(cls, list_name: str):
        """
        根据ID获取名单
        :param list_name: list_name
        :return: 名单对象
        """
        return await cls.get(list_name=list_name)

    @classmethod
    async def get_all_wordlists(cls):
        """
        获取所有名单（排除已删除的）
        :return: 名单列表
        """
        return await cls.query_all()

    async def update_wordlist(self, **kwargs):
        """
        更新名单
        :param kwargs: 需要更新的字段
        :return: 更新后的名单对象
        """
        return await self.update(**kwargs)

    async def delete_wordlist(self, delete_by: str = None):
        """
        软删除名单
        :param delete_by: 删除人
        :return: 删除结果
        """
        return await self.delete(delete_by=delete_by)

    async def hard_delete_wordlist(self):
        """
        硬删除名单
        :return: 删除结果
        """
        return await self.hard_delete()
