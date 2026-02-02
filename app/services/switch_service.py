import time

from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.ac_switch import ACSwitch
from yuyan.app.models.ai_switch import AISwitch
from yuyan.app.models.model_threshold import ModelThreshold
from yuyan.app.utils.enums import SwichEnum


def get_ai_switch(db: Session, item_id: int):
    item = db.query(AISwitch).filter(AISwitch.id == item_id, AISwitch.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关内容")
    return item


def get_ai_switchs(db: Session):
    items = db.query(AISwitch).filter(AISwitch.delete_time.is_(None)).all()
    if not items:
        raise NotFound(message="没有找到相关内容")
    return items


def create_ai_switch(db: Session, ctx, form):
    exist = db.query(AISwitch).filter(AISwitch.game_id == form.game_id.data, AISwitch.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="信息已存在")
    item = AISwitch(
        switch=SwichEnum[form.switch.data].value,
        game_id=form.game_id.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(item)
    db.commit()
    k = f"GC_{form.game_id.data}_all"
    ctx.redis.hset(k, "ai_switch", SwichEnum[form.switch.data].value)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ai_switch": int(time.time())})
    return True


def update_ai_switch(db: Session, ctx, item_id: int, form):
    item = get_ai_switch(db, item_id)
    item.switch = SwichEnum[form.switch.data].value
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_all"
    ctx.redis.hset(k, "ai_switch", SwichEnum[form.switch.data].value)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ai_switch": int(time.time())})
    return True


def delete_ai_switch(db: Session, ctx, item_id: int):
    item = get_ai_switch(db, item_id)
    item.soft_delete()
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_all"
    ctx.redis.hdel(k, "ai_switch")
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ai_switch": int(time.time())})
    return True


def get_ac_switch(db: Session, item_id: int):
    item = db.query(ACSwitch).filter(ACSwitch.id == item_id, ACSwitch.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关内容")
    return item


def get_ac_switchs(db: Session):
    items = db.query(ACSwitch).filter(ACSwitch.delete_time.is_(None)).all()
    if not items:
        raise NotFound(message="没有找到相关内容")
    return items


def create_ac_switch(db: Session, ctx, form):
    exist = db.query(ACSwitch).filter(ACSwitch.game_id == form.game_id.data, ACSwitch.delete_time.is_(None)).first()
    if exist:
        raise ParameterException(message="信息已存在")
    item = ACSwitch(
        switch=SwichEnum[form.switch.data].value,
        game_id=form.game_id.data,
        channel=form.channel.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(item)
    db.commit()
    k = f"GC_{form.game_id.data}_{form.channel.data}"
    ctx.redis.hset(k, "ac_switch", SwichEnum[form.switch.data].value)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ac_switch": int(time.time())})
    return True


def update_ac_switch(db: Session, ctx, item_id: int, form):
    item = get_ac_switch(db, item_id)
    item.switch = SwichEnum[form.switch.data].value
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_{item.channel}"
    ctx.redis.hset(k, "ac_switch", SwichEnum[form.switch.data].value)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ac_switch": int(time.time())})
    return True


def delete_ac_switch(db: Session, ctx, item_id: int):
    item = get_ac_switch(db, item_id)
    item.soft_delete()
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_{item.channel}"
    ctx.redis.hdel(k, "ac_switch")
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|ac_switch": int(time.time())})
    return True


def get_threshold(db: Session, item_id: int):
    item = db.query(ModelThreshold).filter(ModelThreshold.id == item_id, ModelThreshold.delete_time.is_(None)).first()
    if not item:
        raise NotFound(message="没有找到相关内容")
    return item


def get_thresholds(db: Session):
    items = db.query(ModelThreshold).filter(ModelThreshold.delete_time.is_(None)).all()
    if not items:
        raise NotFound(message="没有找到相关内容")
    return items


def create_threshold(db: Session, ctx, form):
    exist = db.query(ModelThreshold).filter(
        ModelThreshold.game_id == form.game_id.data, ModelThreshold.delete_time.is_(None)
    ).first()
    if exist:
        raise ParameterException(message="信息已存在")
    item = ModelThreshold(
        game_id=form.game_id.data,
        threshold=form.threshold.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(item)
    db.commit()
    k = f"GC_{form.game_id.data}_all"
    ctx.redis.hset(k, "model_threshold", form.threshold.data)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|model_threshold": int(time.time())})
    return True


def update_threshold(db: Session, ctx, item_id: int, form):
    item = get_threshold(db, item_id)
    item.threshold = form.threshold.data
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_all"
    ctx.redis.hset(k, "model_threshold", form.threshold.data)
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|model_threshold": int(time.time())})
    return True


def delete_threshold(db: Session, ctx, item_id: int):
    item = get_threshold(db, item_id)
    item.soft_delete()
    db.add(item)
    db.commit()
    k = f"GC_{item.game_id}_all"
    ctx.redis.hdel(k, "model_threshold")
    ctx.redis.zadd("waiting_update_gc_list", {f"{k}|model_threshold": int(time.time())})
    return True
