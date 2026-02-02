import json
import pickle
import time

from fastapi import APIRouter, Depends, Request

from yuyan.app.api.deps import get_ctx, get_db
from yuyan.app.core.exceptions import NotFound
from yuyan.app.utils.cache_sql_data import sql_data_to_redis
from yuyan.app.services.cache import load_cache_from_redis, load_chat_sentinel, update_cache_data
from yuyan.app.services.response import success_response

router = APIRouter(prefix="/base")


@router.get("/local_cache_games")
def local_cache_games(ctx=Depends(get_ctx)):
    return ctx.config.get("ALL_GAMES", [])


@router.get("/local_cache_gc")
def local_cache_gc(ctx=Depends(get_ctx)):
    return ctx.config.get("GAME_CHANNEL", {})


@router.get("/local_cache_data")
def local_cache_data(ctx=Depends(get_ctx)):
    cache_data = ctx.config.get("CACHE_DATA", {})
    safe_data = {}
    for k, v in cache_data.items():
        data = v.get("data", "")
        v_copy = dict(v)
        v_copy["data"] = "ACTree" if data else ""
        safe_data[k] = v_copy
    return safe_data


@router.get("/update_cache")
def update_cache(ctx=Depends(get_ctx)):
    update_cache_data(ctx)
    return success_response(msg="ok")


@router.get("/sql2redis")
def sql2redis(ctx=Depends(get_ctx)):
    redis_url = ctx.config.get("REDIS_URL")
    mysql_url = ctx.config.get("SQLALCHEMY_DATABASE_URI")
    sql_data_to_redis(redis_url=redis_url, mysql_url=mysql_url)
    return success_response(msg="ok")


@router.get("/redis/update_local_games")
def update_local_games_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    ctx.config["ALL_GAMES"] = list(redis_client.smembers("all_games"))
    return success_response(msg="更新本地内存成功")


@router.get("/redis/games")
def get_games_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return list(redis_client.smembers("all_games"))


@router.get("/redis/update_local_gc")
def update_local_gc_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    _, local_gc, _, _, _ = load_cache_from_redis(redis_client)
    ctx.config["GAME_CHANNEL"] = local_gc
    return success_response(msg="更新本地内存成功")


@router.get("/redis/waiting_update_list_detail")
def get_waiting_update_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    list_detail = []
    t = int(time.time())
    num_detail = redis_client.zcount("waiting_update_list_detail", min=t - 500, max=t)
    if num_detail:
        for i in redis_client.zrevrangebyscore("waiting_update_list_detail", min=t - 500, max=t):
            list_detail.append(i)
    return list_detail


@router.get("/redis/waiting_update_gc_list")
def get_waiting_update_gc_list(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    gc_list = []
    t = int(time.time())
    num_gc = redis_client.zcount("waiting_update_gc_list", min=t - 500, max=t)
    if num_gc:
        for i in redis_client.zrevrangebyscore("waiting_update_gc_list", min=t - 500, max=t):
            gc_list.append(i)
    return gc_list


@router.get("/redis/game_channel")
def get_gc_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_gc_listname = {}
    for i in redis_client.scan_iter():
        if i[:3] == "GC_":
            v = redis_client.hgetall(i)
            for k, ve in v.items():
                if k == "swich_shumei":
                    v[k] = ve
                else:
                    v[k] = json.loads(ve) if isinstance(ve, str) else ve
            local_gc_listname[i] = v
    return local_gc_listname


@router.get("/redis/update_local_detail")
def update_local_detail_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_list_data = {}
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_gc_list", "all_games"]:
            continue
        if i[:3] == "GC_" or i[:13] == "chat_sentinel":
            continue
        v = redis_client.hgetall(i)
        raw = v.get("data")
        if raw:
            if isinstance(raw, str):
                data = pickle.loads(raw.encode("latin1"))
            else:
                data = raw
        else:
            data = ""
        v["data"] = data
        local_list_data[i] = v
    ctx.config["CACHE_DATA"] = local_list_data
    return success_response(msg="更新本地内存成功")


@router.get("/redis/list_detail")
def get_redis_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_list_data = {}
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_gc_list", "all_games"]:
            continue
        if i[:3] == "GC_" or i[:13] == "chat_sentinel":
            continue
        v = redis_client.hgetall(i)
        v["data"] = "ACTree" if v.get("data") else ""
        local_list_data[i] = v
    return local_list_data


@router.get("/mysql/update_local_games")
def update_local_games_from_mysql(db=Depends(get_db), ctx=Depends(get_ctx)):
    from yuyan.app.services import game_service

    games = game_service.get_games(db)
    ctx.config["ALL_GAMES"] = [i.game_id for i in games]
    return success_response(msg="更新本地内存成功")


@router.get("/redis/waiting_update_gc_list/reset")
def reset_waiting_update_gc_list(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    for i in redis_client.scan_iter():
        if i[:3] == "GC_":
            v = redis_client.hgetall(i)
            for k in v.keys():
                redis_client.zadd("waiting_update_gc_list", {f"{i}|{k}": int(time.time())})
    return success_response(msg="重置成功")


@router.get("/redis/waiting_update_list_detail/reset")
def reset_waiting_update_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_gc_list", "all_games"]:
            continue
        if i[:3] == "GC_" or i[:13] == "chat_sentinel":
            continue
        redis_client.zadd("waiting_update_list_detail", {i: int(time.time())})
    return success_response(msg="重置成功")


@router.get("/redis/chat_sentinel/account")
def get_chat_sentinel_account(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return redis_client.hgetall("chat_sentinel_account_id")


@router.get("/redis/chat_sentinel/ip")
def get_chat_sentinel_ip(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return redis_client.hgetall("chat_sentinel_ip")


@router.get("/redis/dun_secret")
def get_dun_secret(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return redis_client.hgetall("dun_secret")


@router.get("/redis/chat_sentinel/ip/reset")
def reset_chat_sentinel_ip(request: Request, ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    rule = request.query_params.get("rule")
    if not rule:
        raise NotFound(msg="未找到相关数据")
    data = redis_client.hget("chat_sentinel_ip", rule)
    if not data:
        raise NotFound(msg="未找到相关数据")
    redis_client.hset("chat_sentinel_ip", rule, json.dumps({}))
    ctx.config["CHAT_SENTINEL"] = load_chat_sentinel(redis_client)
    return success_response(msg="重置成功")


@router.get("/redis/chat_sentinel/account/reset")
def reset_chat_sentinel_account(request: Request, ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    rule = request.query_params.get("rule")
    if not rule:
        raise NotFound(msg="未找到相关数据")
    data = redis_client.hget("chat_sentinel_account_id", rule)
    if not data:
        raise NotFound(msg="未找到相关数据")
    redis_client.hset("chat_sentinel_account_id", rule, json.dumps({}))
    ctx.config["CHAT_SENTINEL"] = load_chat_sentinel(redis_client)
    return success_response(msg="重置成功")
