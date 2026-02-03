import pickle
import time
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.exceptions import NotFound, ParameterException
from app.models.list_detail import ListDetail
from app.utils.ahocorasick_utils import build_actree
from app.utils.enums import ListMatchTypeEnum
from app.utils.tokenizer import AllTokenizer

tokenizer = AllTokenizer()


def get_detail(db: Session, detail_id: int):
    detail = db.query(ListDetail).filter(ListDetail.id == detail_id, ListDetail.delete_time.is_(None)).first()
    if not detail:
        raise NotFound(message="没有找到相关文本")
    return detail


def get_detail_by_text(db: Session, text: str):
    details = db.query(ListDetail).filter(ListDetail.text == text, ListDetail.delete_time.is_(None)).all()
    if not details:
        raise NotFound(message="没有找到相关文本")
    return details


def get_all(db: Session):
    details = db.query(ListDetail).filter(ListDetail.delete_time.is_(None)).all()
    if not details:
        raise NotFound(message="没有找到相关文本")
    return details


def add_detail(db: Session, ctx, name_list, form):
    exist = (
        db.query(ListDetail)
        .filter(ListDetail.list_no == name_list.no, ListDetail.text == form.text.data, ListDetail.delete_time.is_(None))
        .first()
    )
    if exist:
        raise ParameterException(message="文本已存在")

    _add_redis_data(ctx, name_list, form.text.data)
    detail = ListDetail(
        list_id=name_list.id,
        list_no=name_list.no,
        text=form.text.data,
        memo=form.memo.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(detail)
    db.commit()
    return True


def update_detail(db: Session, ctx, detail, name_list, form):
    exist = (
        db.query(ListDetail)
        .filter(
            ListDetail.list_no == name_list.no,
            ListDetail.text == form.text.data,
            ListDetail.id != detail.id,
            ListDetail.delete_time.is_(None),
        )
        .first()
    )
    if exist:
        raise ParameterException(message="文本已存在")

    _update_redis_word(ctx, name_list, detail.text, form.text.data)
    detail.text = form.text.data
    detail.memo = form.memo.data
    detail.update_by = form.username.data
    db.add(detail)
    db.commit()
    return True


def remove_detail_by_text(db: Session, ctx, name_list, text: str):
    detail = (
        db.query(ListDetail)
        .filter(ListDetail.list_no == name_list.no, ListDetail.text == text, ListDetail.delete_time.is_(None))
        .first()
    )
    if not detail:
        raise NotFound(message="没有找到相关文本")
    _remove_redis_word(ctx, name_list, detail.text)
    detail.soft_delete()
    db.add(detail)
    db.commit()
    return True


def remove_detail(db: Session, ctx, detail, name_list, form):
    _remove_redis_word(ctx, name_list, detail.text)
    detail.soft_delete(form.username.data)
    db.add(detail)
    db.commit()
    return True


def add_batch_detail(db: Session, ctx, name_list, form):
    text_list = list(set(form.data.data))
    new_text = []
    for text in text_list:
        exist = (
            db.query(ListDetail)
            .filter(ListDetail.list_no == name_list.no, ListDetail.text == text, ListDetail.delete_time.is_(None))
            .first()
        )
        if exist:
            continue
        new_text.append(text)
        detail = ListDetail(
            list_id=name_list.id,
            list_no=name_list.no,
            text=text,
            memo="",
            create_by=form.username.data,
            update_by=form.username.data,
            create_time=datetime.now(),
            update_time=datetime.now(),
        )
        db.add(detail)
    if new_text:
        _add_batch_redis_data(ctx, name_list, new_text)
    db.commit()
    return True


def remove_batch_detail(db: Session, ctx, name_list, form):
    details = db.query(ListDetail).filter(ListDetail.id.in_(form.ids.data), ListDetail.delete_time.is_(None)).all()
    if not details:
        raise ParameterException(message="数据不存在")
    for detail in details:
        _remove_redis_word(ctx, name_list, detail.text)
        detail.soft_delete(form.username.data)
        db.add(detail)
    db.commit()
    return True


def validate_ids(db: Session, ids):
    details = db.query(ListDetail).filter(ListDetail.id.in_(ids), ListDetail.delete_time.is_(None)).distinct().all()
    if not details:
        raise ParameterException(message="数据不存在")
    list_set = list(set([i.list_no for i in details]))
    if len(list_set) != 1:
        raise ParameterException(message="数据存在异常, 删除失败")
    return details[0]


def _serialize_actree(actree):
    try:
        return pickle.dumps(actree).decode("latin1")
    except Exception:
        return actree


def _load_actree(raw):
    if isinstance(raw, str):
        return pickle.loads(raw.encode("latin1"))
    return raw


def _add_redis_data(ctx, name_list, raw_text):
    redis_client = ctx.redis
    list_no = name_list.no
    match_type = ListMatchTypeEnum(name_list._match_type)
    if match_type == ListMatchTypeEnum.SEMANTIC:
        filter_text = tokenizer.tokenize(raw_text, drop_prun=True, language=name_list.language)
    else:
        filter_text = raw_text
    if redis_client.exists(list_no):
        if redis_client.hexists(list_no, "data"):
            data = redis_client.hget(list_no, "data")
            ac_data = _load_actree(data)
            ac_data.add_word(filter_text, (filter_text, raw_text))
            ac_data.make_automaton()
            redis_client.hset(list_no, "data", _serialize_actree(ac_data))
        else:
            redis_client.hset(list_no, "data", _serialize_actree(build_actree([(filter_text, raw_text)])))
    else:
        r = {
            "name": name_list.name,
            "type": name_list._type,
            "match_rule": name_list._match_rule,
            "match_type": name_list._match_type,
            "suggest": name_list._suggest,
            "risk_type": name_list._risk_type,
            "status": int(name_list._status),
            "language": name_list.language,
            "data": _serialize_actree(build_actree([(filter_text, raw_text)])),
        }
        redis_client.hset(list_no, mapping=r)
    redis_client.zadd("waiting_update_list_detail", {list_no: int(time.time())})


def _add_batch_redis_data(ctx, name_list, text_list):
    redis_client = ctx.redis
    list_no = name_list.no
    match_type = ListMatchTypeEnum(name_list._match_type)
    if match_type == ListMatchTypeEnum.SEMANTIC:
        language = name_list.language
        filter_text_list = [(tokenizer.tokenize(i, drop_prun=True, language=language), i) for i in text_list]
    else:
        filter_text_list = [(i, i) for i in text_list]

    if redis_client.exists(list_no):
        if redis_client.hexists(list_no, "data"):
            data = redis_client.hget(list_no, "data")
            ac_data = _load_actree(data)
            for i in filter_text_list:
                ac_data.add_word(i[0], (i[0], i[1]))
            ac_data.make_automaton()
            redis_client.hset(list_no, "data", _serialize_actree(ac_data))
        else:
            ac_data = build_actree(filter_text_list)
            redis_client.hset(list_no, "data", _serialize_actree(ac_data))
    else:
        ac_data = build_actree(filter_text_list)
        r = {
            "name": name_list.name,
            "type": name_list._type,
            "match_rule": name_list._match_rule,
            "match_type": name_list._match_type,
            "suggest": name_list._suggest,
            "risk_type": name_list._risk_type,
            "status": int(name_list._status),
            "language": name_list.language,
            "data": _serialize_actree(ac_data),
        }
        redis_client.hset(list_no, mapping=r)
    redis_client.zadd("waiting_update_list_detail", {list_no: int(time.time())})


def _remove_redis_word(ctx, name_list, text):
    redis_client = ctx.redis
    list_no = name_list.no
    if not redis_client.exists(list_no):
        return
    data = redis_client.hget(list_no, "data")
    if not data:
        return
    ac_data = _load_actree(data)
    match_type = ListMatchTypeEnum(name_list._match_type)
    if match_type == ListMatchTypeEnum.SEMANTIC:
        filter_text = tokenizer.tokenize(text, drop_prun=True, language=name_list.language)
    else:
        filter_text = text
    try:
        ac_data.remove_word(filter_text)
        ac_data.make_automaton()
        redis_client.hset(list_no, "data", _serialize_actree(ac_data))
        redis_client.zadd("waiting_update_list_detail", {list_no: int(time.time())})
    except Exception:
        return


def _update_redis_word(ctx, name_list, old_text, new_text):
    redis_client = ctx.redis
    list_no = name_list.no
    if not redis_client.exists(list_no):
        return
    data = redis_client.hget(list_no, "data")
    if not data:
        return
    ac_data = _load_actree(data)
    match_type = ListMatchTypeEnum(name_list._match_type)
    if match_type == ListMatchTypeEnum.SEMANTIC:
        old_filter_text = tokenizer.tokenize(old_text, drop_prun=True, language=name_list.language)
        new_filter_text = tokenizer.tokenize(new_text, drop_prun=True, language=name_list.language)
    else:
        old_filter_text = old_text
        new_filter_text = new_text
    ac_data.remove_word(old_filter_text)
    ac_data.add_word(new_filter_text, (new_filter_text, new_text))
    ac_data.make_automaton()
    redis_client.hset(list_no, "data", _serialize_actree(ac_data))
    redis_client.zadd("waiting_update_list_detail", {list_no: int(time.time())})
