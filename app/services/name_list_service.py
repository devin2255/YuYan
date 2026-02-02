import json
import time
import uuid

from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.list_detail import ListDetail
from yuyan.app.models.list_game_channel import ListGameChannel
from yuyan.app.models.name_list import NameList
from yuyan.app.utils.enums import ListStatusEnum


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


def create_name_list(db: Session, ctx, form, games, channels):
    exist = db.query(NameList).filter(NameList.name == form.name.data, NameList.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="名单已存在")
    if not games or not channels or len(games) > 5 or len(channels) > 5:
        raise ParameterException(message="生效游戏不能超过5个, 生效渠道不能超过5个")

    name_list = NameList(
        name=form.name.data,
        no=str(uuid.uuid4()),
        _type=form.type.data,
        _match_rule=form.match_rule.data,
        _match_type=form.match_type.data,
        _suggest=form.suggest.data,
        _risk_type=form.risk_type.data,
        _status=form.status.data,
        language=form.language.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(name_list)
    db.flush()

    _add_relationships(db, ctx, name_list, games, channels)
    _add_detail_redis(ctx, name_list)
    db.commit()
    return True


def update_name_list(db: Session, ctx, lid, form, games, channels):
    name_list = get_name_list(db, lid)
    if not games or not channels or len(games) > 5 or len(channels) > 5:
        raise ParameterException(message="生效游戏不能超过5个, 生效渠道不能超过5个")
    name_list.name = form.name.data
    name_list._type = form.type.data
    name_list._match_rule = form.match_rule.data
    name_list._match_type = form.match_type.data
    name_list._suggest = form.suggest.data
    name_list._risk_type = form.risk_type.data
    name_list._status = form.status.data
    name_list.language = form.language.data
    name_list.update_by = form.username.data
    db.add(name_list)

    _remove_relationships(db, ctx, name_list)
    _add_relationships(db, ctx, name_list, games, channels)
    _update_detail_redis(ctx, name_list, update_data=True)
    db.commit()
    return True


def delete_name_list(db: Session, ctx, lid):
    name_list = get_name_list(db, lid)
    name_list.soft_delete()
    db.add(name_list)
    _remove_relationships(db, ctx, name_list)
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


def _add_relationships(db: Session, ctx, name_list, games, channels):
    for g in games:
        for c in channels:
            rela = ListGameChannel(list_no=name_list.no, game_id=g.game_id, channel_no=c.no)
            db.add(rela)
            _update_gc_redis(ctx, name_list, g.game_id, c.no, add=True)


def _remove_relationships(db: Session, ctx, name_list):
    rels = db.query(ListGameChannel).filter(ListGameChannel.list_no == name_list.no).all()
    for r in rels:
        _update_gc_redis(ctx, name_list, r.game_id, r.channel_no, add=False)
        db.delete(r)


def _update_gc_redis(ctx, name_list, game_id, channel_no, add=True):
    redis_client = ctx.redis
    key = f"GC_{game_id}_{channel_no}"
    list_type = str(name_list._type)
    if redis_client.hexists(key, list_type):
        gc_data = json.loads(redis_client.hget(key, list_type))
    else:
        gc_data = []
    if add:
        if name_list.no not in gc_data:
            gc_data.append(name_list.no)
    else:
        if name_list.no in gc_data:
            gc_data.remove(name_list.no)
    redis_client.hset(key, list_type, json.dumps(list(set(gc_data))))
    redis_client.zadd("waiting_update_gc_list", {f"{key}|{list_type}": int(time.time())})


def _add_detail_redis(ctx, name_list):
    redis_client = ctx.redis
    r = {
        "name": name_list.name,
        "type": name_list._type,
        "match_rule": name_list._match_rule,
        "match_type": name_list._match_type,
        "suggest": name_list._suggest,
        "risk_type": name_list._risk_type,
        "status": int(name_list._status),
        "language": name_list.language,
    }
    redis_client.hset(name_list.no, mapping=r)
    redis_client.zadd("waiting_update_list_detail", {name_list.no: int(time.time())})


def _update_detail_redis(ctx, name_list, update_data=False):
    redis_client = ctx.redis
    if redis_client.exists(name_list.no):
        r = {
            "name": name_list.name,
            "type": name_list._type,
            "match_rule": name_list._match_rule,
            "match_type": name_list._match_type,
            "suggest": name_list._suggest,
            "risk_type": name_list._risk_type,
            "status": int(name_list._status),
            "language": name_list.language,
        }
        redis_client.hset(name_list.no, mapping=r)
        if update_data:
            data = _rebuild_actree(ctx, name_list)
            if data:
                redis_client.hset(name_list.no, "data", data)
        redis_client.zadd("waiting_update_list_detail", {name_list.no: int(time.time())})


def _switch_detail_redis(ctx, name_list):
    redis_client = ctx.redis
    if redis_client.exists(name_list.no):
        redis_client.hset(name_list.no, "status", int(name_list._status))
        redis_client.zadd("waiting_update_list_detail", {name_list.no: int(time.time())})


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
    redis_client.zadd("waiting_update_list_detail", {name_list.no: int(time.time())})
