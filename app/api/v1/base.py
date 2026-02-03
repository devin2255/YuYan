import json
import pickle
import time

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_ctx, get_db
from app.core.exceptions import NotFound
from app.utils.cache_sql_data import sql_data_to_redis
from app.services.cache import load_cache_from_redis, load_chat_sentinel, update_cache_data
from app.services.response import success_response

router = APIRouter(prefix="/cache")


@router.get("/apps")
def local_cache_apps(ctx=Depends(get_ctx)):
    return ctx.config.get("ALL_APPS", [])


@router.get("/app-channels")
def local_cache_app_channel(ctx=Depends(get_ctx)):
    return ctx.config.get("APP_CHANNEL", {})


@router.get("/list-data")
def local_cache_data(ctx=Depends(get_ctx)):
    cache_data = ctx.config.get("CACHE_DATA", {})
    safe_data = {}
    for k, v in cache_data.items():
        data = v.get("data", "")
        v_copy = dict(v)
        v_copy["data"] = "ACTree" if data else ""
        safe_data[k] = v_copy
    return safe_data


@router.post("/refresh")
def update_cache(ctx=Depends(get_ctx)):
    update_cache_data(ctx)
    return success_response(msg="ok")


@router.post("/redis/import")
def sql2redis(ctx=Depends(get_ctx)):
    redis_url = ctx.config.get("REDIS_URL")
    mysql_url = ctx.config.get("SQLALCHEMY_DATABASE_URI")
    sql_data_to_redis(redis_url=redis_url, mysql_url=mysql_url)
    return success_response(msg="ok")


@router.post("/apps/refresh-from-redis")
def update_local_apps_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    ctx.config["ALL_APPS"] = list(redis_client.smembers("all_apps"))
    return success_response(msg="更新本地内存成功")


@router.get("/redis/apps")
def get_apps_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return list(redis_client.smembers("all_apps"))


@router.post("/app-channels/refresh-from-redis")
def update_local_app_channel_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    _, local_app_channel, _, _ = load_cache_from_redis(redis_client)
    ctx.config["APP_CHANNEL"] = local_app_channel
    return success_response(msg="更新本地内存成功")


@router.get("/redis/pending-list-details")
def get_waiting_update_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    list_detail = []
    t = int(time.time())
    num_detail = redis_client.zcount("waiting_update_list_detail", min=t - 500, max=t)
    if num_detail:
        for i in redis_client.zrevrangebyscore("waiting_update_list_detail", min=t - 500, max=t):
            list_detail.append(i)
    return list_detail


@router.get("/redis/pending-app-channels")
def get_waiting_update_app_channel_list(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    app_channel_list = []
    t = int(time.time())
    num_app_channel = redis_client.zcount("waiting_update_app_channel_list", min=t - 500, max=t)
    if num_app_channel:
        for i in redis_client.zrevrangebyscore("waiting_update_app_channel_list", min=t - 500, max=t):
            app_channel_list.append(i)
    return app_channel_list


@router.get("/redis/app-channels")
def get_app_channel_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_app_channel_listname = {}
    for i in redis_client.scan_iter():
        if i[:3] == "AC_":
            v = redis_client.hgetall(i)
            for k, ve in v.items():
                if k == "swich_shumei":
                    v[k] = ve
                else:
                    v[k] = json.loads(ve) if isinstance(ve, str) else ve
            local_app_channel_listname[i] = v
    return local_app_channel_listname


@router.post("/list-data/refresh-from-redis")
def update_local_detail_from_redis(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_list_data = {}
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_app_channel_list", "all_apps"]:
            continue
        if i[:3] == "AC_" or i[:13] == "chat_sentinel":
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


@router.get("/redis/list-data")
def get_redis_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    local_list_data = {}
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_app_channel_list", "all_apps"]:
            continue
        if i[:3] == "AC_" or i[:13] == "chat_sentinel":
            continue
        v = redis_client.hgetall(i)
        v["data"] = "ACTree" if v.get("data") else ""
        local_list_data[i] = v
    return local_list_data


@router.post("/apps/refresh-from-db")
def update_local_apps_from_mysql(db=Depends(get_db), ctx=Depends(get_ctx)):
    from app.services import app_service

    apps = app_service.get_apps(db)
    ctx.config["ALL_APPS"] = [i.app_id for i in apps]
    return success_response(msg="更新本地内存成功")


@router.post("/redis/pending-app-channels/reset")
def reset_waiting_update_app_channel_list(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    for i in redis_client.scan_iter():
        if i[:3] == "AC_":
            v = redis_client.hgetall(i)
            for k in v.keys():
                redis_client.zadd("waiting_update_app_channel_list", {f"{i}|{k}": int(time.time())})
    return success_response(msg="重置成功")


@router.post("/redis/pending-list-details/reset")
def reset_waiting_update_list_detail(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    for i in redis_client.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_app_channel_list", "all_apps"]:
            continue
        if i[:3] == "AC_" or i[:13] == "chat_sentinel":
            continue
        redis_client.zadd("waiting_update_list_detail", {i: int(time.time())})
    return success_response(msg="重置成功")


@router.get("/redis/chat-sentinel/accounts")
def get_chat_sentinel_account(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return redis_client.hgetall("chat_sentinel_account_id")


@router.get("/redis/chat-sentinel/ips")
def get_chat_sentinel_ip(ctx=Depends(get_ctx)):
    redis_client = ctx.redis
    return redis_client.hgetall("chat_sentinel_ip")


@router.post("/redis/chat-sentinel/ips/reset")
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


@router.post("/redis/chat-sentinel/accounts/reset")
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
