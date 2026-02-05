import json
from typing import List, Tuple

from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.api.deps import get_ctx, get_db, get_current_user
from app.core.exceptions import ParameterException
from app.schemas.name_list import CreateOrUpdateNameList, SwitchNameList
from app.services import channel_service, app_service, name_list_service
from app.services.response import success_response
from app.services.serializer import to_dict
from app.services.validators import FormProxy
from app.utils.enums import ListLanguageScopeEnum, ListScopeEnum

router = APIRouter(prefix="/name-lists", dependencies=[Depends(get_current_user)])


def normalize_list(value) -> List[str]:
    if isinstance(value, list):
        return [i for i in value if i not in (None, "", [])]
    if isinstance(value, str):
        if value.startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return [i for i in parsed if i not in (None, "", [])]
                return []
            except Exception:
                pass
        return [i for i in value.split(",") if i]
    if value is None:
        return []
    return []


def normalize_scope(scope: str) -> str:
    if not scope or not isinstance(scope, str):
        raise ParameterException(message="scope 不能为空")
    scope_value = scope.strip().upper()
    try:
        return ListScopeEnum(scope_value).value
    except Exception:
        raise ParameterException(message="scope 不合法")


def normalize_language_scope(scope: str) -> str:
    if not scope or not isinstance(scope, str):
        raise ParameterException(message="language_scope 不能为空")
    scope_value = scope.strip().upper()
    try:
        return ListLanguageScopeEnum(scope_value).value
    except Exception:
        raise ParameterException(message="language_scope 不合法")


def normalize_language_codes(value) -> List[str]:
    codes = normalize_list(value)
    normalized = []
    for item in codes:
        if item is None:
            continue
        code = str(item).strip().lower()
        if not code:
            continue
        if code not in normalized:
            normalized.append(code)
    return normalized


def process_language(language_scope_raw, language_codes_raw, legacy_language_raw=None) -> Tuple[str, List[str]]:
    if language_scope_raw is not None:
        scope_value = normalize_language_scope(language_scope_raw)
        codes = normalize_language_codes(language_codes_raw)
    else:
        legacy = str(legacy_language_raw).strip().lower() if legacy_language_raw else ""
        if legacy and legacy != "all":
            scope_value = ListLanguageScopeEnum.SPECIFIC.value
            codes = [legacy]
        else:
            scope_value = ListLanguageScopeEnum.ALL.value
            codes = []

    if scope_value == ListLanguageScopeEnum.ALL.value:
        if codes:
            raise ParameterException(message="language_scope=ALL 不允许传 language_codes")
    elif scope_value == ListLanguageScopeEnum.SPECIFIC.value:
        if not codes:
            raise ParameterException(message="language_scope=SPECIFIC 必须传 language_codes")
    else:
        raise ParameterException(message="language_scope 不合法")
    return scope_value, codes


def process_scope(
    db: Session,
    scope: str,
    app_ids_raw,
    channel_ids_raw,
) -> Tuple[List[str], List[int], str]:
    scope_value = normalize_scope(scope)
    app_ids = normalize_list(app_ids_raw)
    channel_ids = normalize_list(channel_ids_raw)

    if scope_value == ListScopeEnum.GLOBAL.value:
        if app_ids or channel_ids:
            raise ParameterException(message="GLOBAL 作用域不允许传 app_ids/channel_ids")
        return [], [], scope_value

    if scope_value == ListScopeEnum.APP.value:
        if not app_ids:
            raise ParameterException(message="APP 作用域必须传 app_ids")
        if channel_ids:
            raise ParameterException(message="APP 作用域不允许传 channel_ids")
        if len(app_ids) > 5:
            raise ParameterException(message="生效应用不能超过5个")
        app_ids_str = [str(gid) for gid in app_ids]
        for gid in app_ids_str:
            app_service.get_app(db, gid)
        return app_ids_str, [], scope_value

    if scope_value == ListScopeEnum.APP_CHANNEL.value:
        if not app_ids or not channel_ids:
            raise ParameterException(message="APP_CHANNEL 作用域必须传 app_ids 和 channel_ids")
        if len(app_ids) > 5 or len(channel_ids) > 5:
            raise ParameterException(message="生效应用不能超过5个, 生效渠道不能超过5个")
        app_ids_str = [str(gid) for gid in app_ids]
        for gid in app_ids_str:
            app_service.get_app(db, gid)
        try:
            channel_ids_int = [int(cid) for cid in channel_ids]
        except Exception:
            raise ParameterException(message="channel_ids 不合法")
        for cid in channel_ids_int:
            channel_service.get_channel(db, cid)
        return app_ids_str, channel_ids_int, scope_value

    raise ParameterException(message="scope 不合法")


@router.get("/{lid}")
def get_name_list(lid: str, db: Session = Depends(get_db)):
    data = name_list_service.get_name_list_by_name(db, lid)
    result = to_dict(data)
    result["language_codes"] = name_list_service.get_language_codes(db, result["no"])
    return result


@router.get("")
def get_name_lists(db: Session = Depends(get_db)):
    data = name_list_service.get_name_lists(db)
    result = to_dict(data)
    for item in result:
        item["language_codes"] = name_list_service.get_language_codes(db, item["no"])
    return result


@router.post("")
async def create_name_list(payload: CreateOrUpdateNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    app_ids, channel_ids, scope = process_scope(
        db, form.scope.data, form.app_ids.data, form.channel_ids.data
    )
    legacy_language = form.language.data if hasattr(form, "language") else None
    language_scope, language_codes = process_language(
        form.language_scope.data, form.language_codes.data, legacy_language
    )
    form.scope.data = scope
    form.language_scope.data = language_scope
    form.language_codes.data = language_codes
    name_list_service.create_name_list(db, ctx, form, app_ids, channel_ids)
    return success_response(msg="新建名单成功")


@router.put("/{lid}")
async def update_name_list(
    lid: str, payload: CreateOrUpdateNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)
):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    app_ids, channel_ids, scope = process_scope(
        db, form.scope.data, form.app_ids.data, form.channel_ids.data
    )
    legacy_language = form.language.data if hasattr(form, "language") else None
    language_scope, language_codes = process_language(
        form.language_scope.data, form.language_codes.data, legacy_language
    )
    form.scope.data = scope
    form.language_scope.data = language_scope
    form.language_codes.data = language_codes
    name_list_service.update_name_list(db, ctx, lid, form, app_ids, channel_ids)
    return success_response(msg="更新名单成功")


@router.delete("/{lid}")
def delete_name_list(lid: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    name_list_service.delete_name_list(db, ctx, lid)
    return success_response(msg="删除名单成功")


@router.patch("/{lid}/status")
async def switch_name_list(lid: str, payload: SwitchNameList, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    form_data = payload
    form = FormProxy(**form_data.model_dump())
    name_list_service.switch_name_list(db, ctx, lid, form)
    return success_response(msg="名单状态修改成功")
