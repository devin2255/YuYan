from fastapi import HTTPException
from tortoise.exceptions import DoesNotExist

from app.api import BluePrint
from app.models.wordlist import WordList
from app.validators.wordlist import CreateOrUpdateWordListRequest

wordlist_api = BluePrint('wordlist')


@wordlist_api.route('', methods=["GET"])
async def get_wordlists():
    """
    获取所有名单。
    """
    try:
        wordlists = await WordList.get_all_wordlists()
        return wordlists
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wordlist_api.route('/{wordlist_id}', methods=["GET"])
async def get_wordlist(wordlist_id: int):
    """
    根据ID获取单个名单。
    """
    try:
        wordlist = await WordList.get_wordlist_by_id(wordlist_id)
        if not wordlist:
            raise HTTPException(status_code=404, detail="名单未找到")
        return wordlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wordlist_api.route('', methods=["POST"])
async def create_wordlist(request: CreateOrUpdateWordListRequest):
    """
    创建新名单。
    """
    try:
        # 检查 app_id 是否已存在
        existing_app = await WordList.get_wordlist_by_name(request.list_name)
        if existing_app:
            raise HTTPException(status_code=400, detail="名单已存在")
    except DoesNotExist:
        pass  # list_name 不存在，可以继续创建

    try:
        kwargs = request.model_dump()
        if request.username:
            kwargs['create_by'] = request.username
            kwargs['update_by'] = request.username
        wordlist = await WordList.create_wordlist(**kwargs)
        return wordlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wordlist_api.route('/{wordlist_id}', methods=["PUT"])
async def update_wordlist(wordlist_id: int, request: CreateOrUpdateWordListRequest):
    """
    更新名单。
    """
    try:
        wordlist = await WordList.get_wordlist_by_id(wordlist_id)
        if not wordlist:
            raise HTTPException(status_code=404, detail="名单未找到")

        # 过滤掉值为 None 的字段
        update_data = {k: v for k, v in request.model_dump().items() if v is not None}
        if request.username:
            update_data['update_by'] = request.username
        await wordlist.update_wordlist(**update_data)
        return wordlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@wordlist_api.route('/{wordlist_id}', methods=["DELETE"])
async def delete_wordlist(wordlist_id: int):
    """
    删除名单。
    """
    try:
        wordlist = await WordList.get_wordlist_by_id(wordlist_id)
        if not wordlist:
            raise HTTPException(status_code=404, detail="名单未找到")

        await wordlist.delete_wordlist()
        return {"message": "名单删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
