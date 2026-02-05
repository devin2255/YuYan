import json
import time
import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFound, ParameterException
from app.models.list_detail import ListDetail
from app.models.list_app_channel import ListAppChannel
from app.models.name_list_language import NameListLanguage
from app.models.name_list import NameList
from app.utils.enums import ListLanguageScopeEnum, ListScopeEnum, ListStatusEnum
from app.services.cache import bump_list_detail_version


def get_name_list(db: Session, lid: str):
    item = db.query(NameList).filter(NameList.id == lid, NameList.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关名单")
    return item


def get_name_list_by_no(db: Session, list_no: str):
    item = db.query(NameList).filter(NameList.no == list_no, NameList.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关名单")
    return item


def get_name_list_by_name(db: Session, name: str):
    item = db.query(NameList).filter(NameList.name == name, NameList.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关名单")
    return item


def get_name_lists(db: Session):
    items = db.query(NameList).filter(NameList.delete_time.is_(None)).all()
    if not items:
        raise NotFound(message="没有找到相关名单")
    return items


def get_language_codes(db: Session, list_no: str):
    rows = (
        db.query(NameListLanguage)
        .filter(NameListLanguage.list_no == list_no, NameListLanguage.delete_time.is_(None))
        .all()
    )
    return [row.language_code for row in rows]


def create_name_list(db: Session, ctx, form, app_ids, channel_ids):
    exist = db.query(NameList).filter(NameList.name == form.name.data, NameList.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="名单已存在")
    scope_value = _validate_scope_inputs(form.scope.data, app_ids, channel_ids)
    legacy_language = form.language.data if hasattr(form, "language") else None
    language_scope, language_codes, tokenize_language = _resolve_language(
        form.language_scope.data, form.language_codes.data, legacy_language
    )

    name_list = NameList(
        name=form.name.data,
        no=str(uuid.uuid4()),
        _type=form.type.data,
        _match_rule=form.match_rule.data,
        _match_type=form.match_type.data,
        _suggest=form.suggest.data,
        _risk_type=form.risk_type.data,
        _status=form.status.data,
        language=tokenize_language,
        scope=scope_value,
        language_scope=language_scope,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(name_list)
    db.flush()

    _add_relationships(db, ctx, name_list, app_ids, channel_ids)
    _replace_language_codes(db, name_list, language_codes)
    _add_detail_redis(ctx, name_list, language_scope=language_scope, language_codes=language_codes)
    db.commit()
    return True


def update_name_list(db: Session, ctx, lid, form, app_ids, channel_ids):
    name_list = get_name_list(db, lid)
    scope_value = _validate_scope_inputs(form.scope.data, app_ids, channel_ids)
    legacy_language = form.language.data if hasattr(form, "language") else None
    language_scope, language_codes, tokenize_language = _resolve_language(
        form.language_scope.data, form.language_codes.data, legacy_language
    )
    old_scope = name_list.scope
    old_type = name_list._type
    name_list.name = form.name.data
    name_list._type = form.type.data
    name_list._match_rule = form.match_rule.data
    name_list._match_type = form.match_type.data
    name_list._suggest = form.suggest.data
    name_list._risk_type = form.risk_type.data
    name_list._status = form.status.data
    name_list.language = tokenize_language
    name_list.scope = scope_value
    name_list.language_scope = language_scope
    name_list.update_by = form.username.data
    db.add(name_list)

    _remove_relationships(db, ctx, name_list, scope_override=old_scope, list_type_override=old_type)
    _add_relationships(db, ctx, name_list, app_ids, channel_ids)
    _replace_language_codes(db, name_list, language_codes)
    _update_detail_redis(
        ctx,
        name_list,
        update_data=True,
        language_scope=language_scope,
        language_codes=language_codes,
    )
    db.commit()
    return True


def delete_name_list(db: Session, ctx, lid):
    name_list = get_name_list(db, lid)
    name_list.soft_delete()
    db.add(name_list)
    _remove_relationships(db, ctx, name_list)
    _remove_language_codes(db, name_list)
    _remove_list_detail(db, ctx, name_list)
    db.commit()
    return True


def switch_name_list(db: Session, ctx, lid, form):
    name_list = get_name_list(db, lid)
    if ListStatusEnum(form.status.data) == name_list.status:
        return True
    name_list._status = form.status.data
    name_list.update_by = form.username.data
    db.add(name_list)
    _switch_detail_redis(ctx, name_list)
    db.commit()
    return True


def _normalize_scope(scope: str) -> str:
    if not scope:
        raise ParameterException(message="scope 不能为空")
    scope_value = str(scope).strip().upper()
    if scope_value in {
        ListScopeEnum.GLOBAL.value,
        ListScopeEnum.APP.value,
        ListScopeEnum.APP_CHANNEL.value,
    }:
        return scope_value
    raise ParameterException(message="scope 不合法")


def _normalize_language_scope(scope):
    if scope is None or scope == "":
        return None
    scope_value = str(scope).strip().upper()
    if scope_value in {
        ListLanguageScopeEnum.ALL.value,
        ListLanguageScopeEnum.SPECIFIC.value,
    }:
        return scope_value
    raise ParameterException(message="language_scope 不合法")


def _normalize_language_codes(codes):
    if not codes:
        return []
    if isinstance(codes, str):
        raw = codes.strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    codes = parsed
                else:
                    codes = []
            except Exception:
                codes = [i for i in raw.split(",") if i]
        else:
            codes = [i for i in raw.split(",") if i]
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


def _resolve_language(scope_raw, codes_raw, legacy_language=None):
    scope_value = _normalize_language_scope(scope_raw)
    codes = _normalize_language_codes(codes_raw)

    if scope_value is None:
        legacy = str(legacy_language).strip().lower() if legacy_language else ""
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

    tokenize_language = codes[0] if scope_value == ListLanguageScopeEnum.SPECIFIC.value and len(codes) == 1 else "all"
    return scope_value, codes, tokenize_language


def _replace_language_codes(db: Session, name_list: NameList, language_codes):
    db.query(NameListLanguage).filter(NameListLanguage.list_no == name_list.no).delete()
    for code in language_codes:
        db.add(NameListLanguage(list_no=name_list.no, language_code=code))


def _remove_language_codes(db: Session, name_list: NameList) -> None:
    db.query(NameListLanguage).filter(NameListLanguage.list_no == name_list.no).delete()


def _validate_scope_inputs(scope: str, app_ids, channel_ids):
    scope_value = _normalize_scope(scope)
    if scope_value == ListScopeEnum.GLOBAL.value:
        if app_ids or channel_ids:
            raise ParameterException(message="GLOBAL 作用域不允许传 app_ids/channel_ids")
        return scope_value
    if scope_value == ListScopeEnum.APP.value:
        if not app_ids:
            raise ParameterException(message="APP 作用域必须传 app_ids")
        if channel_ids:
            raise ParameterException(message="APP 作用域不允许传 channel_ids")
        if len(app_ids) > 5:
            raise ParameterException(message="生效应用不能超过5个")
        return scope_value
    if scope_value == ListScopeEnum.APP_CHANNEL.value:
        if not app_ids or not channel_ids:
            raise ParameterException(message="APP_CHANNEL 作用域必须传 app_ids 和 channel_ids")
        if len(app_ids) > 5 or len(channel_ids) > 5:
            raise ParameterException(message="生效应用不能超过5个, 生效渠道不能超过5个")
        return scope_value
    raise ParameterException(message="scope 不合法")


def _add_relationships(db: Session, ctx, name_list, app_ids, channel_ids):
    scope = _normalize_scope(name_list.scope)
    if scope == ListScopeEnum.GLOBAL.value:
        rela = ListAppChannel(list_no=name_list.no, app_id=None, channel_id=None)
        db.add(rela)
        _update_app_channel_redis(ctx, name_list, None, None, add=True)
        return

    if scope == ListScopeEnum.APP.value:
        for app_id in app_ids:
            rela = ListAppChannel(list_no=name_list.no, app_id=app_id, channel_id=None)
            db.add(rela)
            _update_app_channel_redis(ctx, name_list, app_id, None, add=True)
        return

    for app_id in app_ids:
        for channel_id in channel_ids:
            rela = ListAppChannel(list_no=name_list.no, app_id=app_id, channel_id=channel_id)
            db.add(rela)
            _update_app_channel_redis(ctx, name_list, app_id, channel_id, add=True)


def _remove_relationships(db: Session, ctx, name_list, scope_override=None, list_type_override=None):
    rels = db.query(ListAppChannel).filter(ListAppChannel.list_no == name_list.no).all()
    scope_value = _normalize_scope(scope_override or name_list.scope)
    list_type_value = list_type_override if list_type_override is not None else name_list._type
    for r in rels:
        _update_app_channel_redis(
            ctx,
            name_list,
            r.app_id,
            r.channel_id,
            add=False,
            scope_override=scope_value,
            list_type_override=list_type_value,
        )
        db.delete(r)


def _build_app_channel_key(scope: str, app_id, channel_id) -> str:
    scope_value = str(scope).upper() if scope else ""
    if scope_value == ListScopeEnum.GLOBAL.value:
        return "AC_all_all"
    if scope_value == ListScopeEnum.APP.value:
        return f"AC_{app_id}_all" if app_id is not None else ""
    if scope_value == ListScopeEnum.APP_CHANNEL.value:
        if app_id is None or channel_id is None:
            return ""
        return f"AC_{app_id}_{channel_id}"
    return ""


def _update_app_channel_redis(
    ctx,
    name_list,
    app_id,
    channel_id,
    add=True,
    scope_override=None,
    list_type_override=None,
):
    redis_client = ctx.redis
    scope_value = _normalize_scope(scope_override or name_list.scope)
    key = _build_app_channel_key(scope_value, app_id, channel_id)
    if not key:
        return
    list_type = str(list_type_override if list_type_override is not None else name_list._type)
    if redis_client.hexists(key, list_type):
        app_channel_data = json.loads(redis_client.hget(key, list_type))
    else:
        app_channel_data = []
    if add:
        if name_list.no not in app_channel_data:
            app_channel_data.append(name_list.no)
    else:
        if name_list.no in app_channel_data:
            app_channel_data.remove(name_list.no)
    redis_client.hset(key, list_type, json.dumps(list(set(app_channel_data))))
    redis_client.zadd("waiting_update_app_channel_list", {f"{key}|{list_type}": int(time.time())})


def _add_detail_redis(ctx, name_list, language_scope=None, language_codes=None):
    redis_client = ctx.redis
    scope_value = _normalize_language_scope(language_scope) or name_list.language_scope or ListLanguageScopeEnum.ALL.value
    codes = _normalize_language_codes(language_codes)
    r = {
        "name": name_list.name,
        "type": name_list._type,
        "match_rule": name_list._match_rule,
        "match_type": name_list._match_type,
        "suggest": name_list._suggest,
        "risk_type": name_list._risk_type,
        "status": int(name_list._status),
        "language": name_list.language,
        "language_scope": scope_value,
        "language_codes": json.dumps(codes),
    }
    redis_client.hset(name_list.no, mapping=r)
    bump_list_detail_version(redis_client, name_list.no)


def _update_detail_redis(ctx, name_list, update_data=False, language_scope=None, language_codes=None):
    redis_client = ctx.redis
    if redis_client.exists(name_list.no):
        scope_value = _normalize_language_scope(language_scope) or name_list.language_scope or ListLanguageScopeEnum.ALL.value
        codes = _normalize_language_codes(language_codes)
        r = {
            "name": name_list.name,
            "type": name_list._type,
            "match_rule": name_list._match_rule,
            "match_type": name_list._match_type,
            "suggest": name_list._suggest,
            "risk_type": name_list._risk_type,
            "status": int(name_list._status),
            "language": name_list.language,
            "language_scope": scope_value,
            "language_codes": json.dumps(codes),
        }
        redis_client.hset(name_list.no, mapping=r)
        if update_data:
            data = _rebuild_actree(ctx, name_list)
            if data:
                redis_client.hset(name_list.no, "data", data)
        bump_list_detail_version(redis_client, name_list.no)


def _switch_detail_redis(ctx, name_list):
    redis_client = ctx.redis
    if redis_client.exists(name_list.no):
        redis_client.hset(name_list.no, "status", int(name_list._status))
        bump_list_detail_version(redis_client, name_list.no)


def _rebuild_actree(ctx, name_list):
    details = (
        ctx.redis.hget(name_list.no, "data")
        if ctx.redis.exists(name_list.no)
        else ""
    )
    if details:
        return details
    return None


def _remove_list_detail(db: Session, ctx, name_list):
    details = db.query(ListDetail).filter(
        ListDetail.list_id == name_list.id,
        ListDetail.delete_time.is_(None),
    ).all()
    for detail in details:
        detail.soft_delete()
        db.add(detail)
    redis_client = ctx.redis
    redis_client.hdel(name_list.no, "data")
    bump_list_detail_version(redis_client, name_list.no)
