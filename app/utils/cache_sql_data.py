import json
import pickle
from urllib.parse import urlparse

import pymysql
import redis

from app.utils.ahocorasick_utils import build_actree
from app.utils.enums import ListLanguageScopeEnum, ListMatchTypeEnum, ListScopeEnum
from app.utils.tokenizer import AllTokenizer

tokenizer = AllTokenizer()


class DataBaseHandle(object):
    def __init__(self, host, username, password, database, port):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.port = port
        self.db = pymysql.connect(
            self.host, self.username, self.password, self.database, self.port, charset="utf8"
        )

    def select(self, sql, return_dict=False):
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor) if return_dict else self.db.cursor()
        try:
            self.cursor.execute(sql)
            data = self.cursor.fetchall()
            res = data
        except Exception:
            res = []
        finally:
            self.cursor.close()
            return res


def cache_from_redis(redis_store):
    local_all_apps = []
    local_list_data = {}
    local_app_channel_listname = {}
    local_access_key = {}

    for i in redis_store.scan_iter():
        if i in [
            "waiting_update_list_detail",
            "waiting_update_app_channel_list",
            "ucache_check_alive_key",
            "list_detail_version_seq",
            "list_detail_version",
            "list_detail_version_index",
        ]:
            continue
        if i[:13] == "chat_sentinel":
            continue
        if i == "all_apps":
            local_all_apps = list(redis_store.smembers(i))
        elif i == "access_key":
            v = redis_store.hgetall(i)
            for k, ve in v.items():
                local_access_key[k] = ve
        elif i[:3] == "AC_":
            v = redis_store.hgetall(i)
            for k, ve in v.items():
                if k == "swich_shumei":
                    v[k] = ve
                else:
                    v[k] = json.loads(ve)
            local_app_channel_listname[i] = v
        else:
            v = redis_store.hgetall(i)
            data = pickle.loads(v["data"].encode("latin1")) if v.get("data") else ""
            v["data"] = data
            local_list_data[i] = v

    local_all_apps = list(set(local_all_apps))
    return local_all_apps, local_app_channel_listname, local_list_data, local_access_key


def sql_data_to_redis(redis_url: str, mysql_url: str):
    if not redis_url or not mysql_url:
        return
    parsed = urlparse(mysql_url.replace("mysql+pymysql", "mysql"))
    db = parsed.path.lstrip("/") if parsed.path else ""
    sql_db = DataBaseHandle(
        host=parsed.hostname,
        port=parsed.port or 3306,
        username=parsed.username,
        password=parsed.password or "",
        database=db,
    )
    redis_store = redis.Redis.from_url(redis_url, decode_responses=True)
    read_sql_all_app(sql_db, redis_store)
    read_sql_app_channel(sql_db, redis_store)
    read_sql_detail_data(sql_db, redis_store)


def read_sql_all_app(sql_db, redis_store):
    sql = """
                SELECT 
                    app_id
                FROM 
                    app
                WHERE
                    delete_time IS NULL
                """
    res = sql_db.select(sql)
    for i in res:
        redis_store.sadd("all_apps", i[0])


def read_sql_app_channel(sql_db, redis_store):
    d = {}
    sql = """
            SELECT 
                list_app_channel.list_no AS list_no, list_app_channel.app_id AS app_id, 
                list_app_channel.channel_id AS channel_id, name_list.type AS list_type,
                name_list.scope AS scope
            FROM 
                list_app_channel, name_list
            WHERE
                list_app_channel.list_no=name_list.no AND list_app_channel.delete_time IS NULL 
        """
    res = sql_db.select(sql, return_dict=True)
    for i in res:
        scope = str(i.get("scope") or ListScopeEnum.APP_CHANNEL.value).upper()
        if scope == ListScopeEnum.GLOBAL.value:
            app_channel = "AC_all_all"
        elif scope == ListScopeEnum.APP.value:
            if not i.get("app_id"):
                continue
            app_channel = "AC_{}_all".format(i["app_id"])
        else:
            if i.get("app_id") is None or i.get("channel_id") is None:
                continue
            app_channel = "AC_{}_{}".format(i["app_id"], i["channel_id"])
        if not d.get(app_channel):
            d[app_channel] = {}
        if d[app_channel].get(i["list_type"]):
            d[app_channel][i["list_type"]].append(i["list_no"])
        else:
            d[app_channel][i["list_type"]] = [i["list_no"]]

    for k, v in d.items():
        for m, n in v.items():
            v[m] = json.dumps(n)
        redis_store.hset(k, mapping=v)
    return True


def read_sql_detail_data(sql_db, redis_store):
    lang_map = {}
    lang_sql = """
            SELECT 
                list_no, language_code
            FROM 
                name_list_language
            WHERE
                delete_time IS NULL
            """
    for item in sql_db.select(lang_sql, return_dict=True):
        list_no = item.get("list_no")
        code = item.get("language_code")
        if not list_no or not code:
            continue
        lang_map.setdefault(list_no, []).append(str(code).strip().lower())

    sql = """
            SELECT 
                *
            FROM 
                name_list
            WHERE
                delete_time IS NULL
            """
    res = sql_db.select(sql, return_dict=True)

    for i in res:
        list_no = i["no"]
        query_detail_sql = """
            SELECT * FROM list_detail WHERE list_no='%s' AND delete_time IS NULL
        """ % list_no
        data = []
        for d in sql_db.select(query_detail_sql, return_dict=True):
            if ListMatchTypeEnum(i["match_type"]) == ListMatchTypeEnum.SEMANTIC:
                filter_text = tokenizer.tokenize(d["text"], drop_prun=True)
            else:
                filter_text = d["text"]
            if filter_text:
                data.append((filter_text, d["text"]))

        language_scope = str(
            i.get("language_scope")
            or (ListLanguageScopeEnum.ALL.value if i.get("language") in [None, "", "all"] else ListLanguageScopeEnum.SPECIFIC.value)
        ).upper()
        language_codes = lang_map.get(list_no, [])
        if language_scope == ListLanguageScopeEnum.SPECIFIC.value and not language_codes:
            legacy = str(i.get("language") or "").strip().lower()
            if legacy and legacy != "all":
                language_codes = [legacy]

        if data:
            ac = build_actree(data)
            ac = pickle.dumps(ac).decode("latin1")
            r = {
                "name": i["name"],
                "type": i["type"],
                "match_rule": i["match_rule"],
                "match_type": i["match_type"],
                "suggest": i["suggest"],
                "risk_type": i["risk_type"],
                "status": i["status"],
                "language": i["language"] if i["language"] else "",
                "language_scope": language_scope,
                "language_codes": json.dumps(language_codes),
                "data": ac,
            }
        else:
            r = {
                "name": i["name"],
                "type": i["type"],
                "match_rule": i["match_rule"],
                "match_type": i["match_type"],
                "suggest": i["suggest"],
                "risk_type": i["risk_type"],
                "status": i["status"],
                "language": i["language"] if i["language"] else "",
                "language_scope": language_scope,
                "language_codes": json.dumps(language_codes),
            }
        redis_store.hset(list_no, mapping=r)
