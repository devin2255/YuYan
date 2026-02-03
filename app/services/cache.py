from __future__ import annotations

import json
import pickle
import random
import time
from typing import Dict, Tuple


def load_cache_from_redis(redis_client) -> Tuple[list, Dict, Dict, Dict]:
    local_all_apps = []
    local_list_data = {}
    local_app_channel_listname = {}
    local_access_key = {}

    for key in redis_client.scan_iter():
        if key in {"waiting_update_list_detail", "waiting_update_app_channel_list", "ucache_check_alive_key"}:
            continue
        if key.startswith("chat_sentinel"):
            continue
        if key == "all_apps":
            local_all_apps = list(redis_client.smembers(key))
            continue
        if key == "access_key":
            local_access_key = redis_client.hgetall(key)
            continue
        if key.startswith("AC_"):
            v = redis_client.hgetall(key)
            for k, ve in v.items():
                if k == "swich_shumei":
                    v[k] = ve
                else:
                    v[k] = json.loads(ve) if isinstance(ve, str) else ve
            local_app_channel_listname[key] = v
            continue

        v = redis_client.hgetall(key)
        raw = v.get("data")
        if raw:
            if isinstance(raw, str):
                data = pickle.loads(raw.encode("latin1"))
            else:
                data = raw
        else:
            data = ""
        v["data"] = data
        local_list_data[key] = v

    local_all_apps = list(set(local_all_apps))
    return local_all_apps, local_app_channel_listname, local_list_data, local_access_key


def process_redis_data(data: Dict) -> Dict:
    result = {}
    if not data:
        return result
    for rule, detail_str in data.items():
        detail = json.loads(detail_str)
        for app, ids in detail.items():
            for item in ids:
                key = f"{app}_{item}"
                result.setdefault(key, []).append(rule)
    return result


def load_chat_sentinel(redis_client) -> Dict:
    account_id_data = redis_client.hgetall("chat_sentinel_account_id")
    ip_data = redis_client.hgetall("chat_sentinel_ip")
    return {
        "account_id": process_redis_data(account_id_data),
        "ip": process_redis_data(ip_data),
    }


def update_cache_data(ctx) -> bool:
    try:
        time_seed = ctx.config.get("TIME_SEED", 0)
        if time_seed:
            time.sleep(random.randint(0, time_seed))
        redis_client = ctx.config["REDIS_CLIENT"]
        # 更新缓存基础数据
        ctx.config["ALL_APPS"] = list(redis_client.smembers("all_apps"))
        ctx.config["ACCESS_KEY"] = redis_client.hgetall("access_key")
        ctx.config["CHAT_SENTINEL"] = load_chat_sentinel(redis_client)

        # 更新 APP_CHANNEL
        t = int(time.time())
        num_app_channel = redis_client.zcount("waiting_update_app_channel_list", min=t - 500, max=t)
        if num_app_channel:
            for item in redis_client.zrevrangebyscore("waiting_update_app_channel_list", min=t - 500, max=t):
                gc, key = item.split("|", 1)
                raw = redis_client.hget(gc, key)
                if key == "swich_shumei":
                    new_data = raw
                else:
                    new_data = json.loads(raw) if isinstance(raw, str) else raw
                ctx.config.setdefault("APP_CHANNEL", {})
                ctx.config["APP_CHANNEL"].setdefault(gc, {})[key] = new_data

        # 更新 CACHE_DATA
        num_detail = redis_client.zcount("waiting_update_list_detail", min=t - 500, max=t)
        if num_detail:
            for list_no in redis_client.zrevrangebyscore("waiting_update_list_detail", min=t - 500, max=t):
                v = redis_client.hgetall(list_no)
                raw = v.get("data")
                if raw:
                    if isinstance(raw, str):
                        data = pickle.loads(raw.encode("latin1"))
                    else:
                        data = raw
                else:
                    data = ""
                v["data"] = data
                ctx.config.setdefault("CACHE_DATA", {})
                ctx.config["CACHE_DATA"][list_no] = v

        # 清理过期记录
        if redis_client.zcount("waiting_update_app_channel_list", min=0, max=t - 500):
            redis_client.zremrangebyscore("waiting_update_app_channel_list", min=0, max=t - 500)
        if redis_client.zcount("waiting_update_list_detail", min=0, max=t - 500):
            redis_client.zremrangebyscore("waiting_update_list_detail", min=0, max=t - 500)
        return True
    except Exception as err:
        ctx.logger.debug(f"update cache err: {err}")
        return False
