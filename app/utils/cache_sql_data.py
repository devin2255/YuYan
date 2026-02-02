import json
import pickle
from urllib.parse import urlparse

import pymysql
import redis

from yuyan.app.utils.ahocorasick_utils import build_actree
from yuyan.app.utils.enums import ListMatchTypeEnum
from yuyan.app.utils.tokenizer import AllTokenizer

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
    local_all_games = []
    local_list_data = {}
    local_gc_listname = {}
    local_access_key = {}
    local_dun_secret = {}

    for i in redis_store.scan_iter():
        if i in ["waiting_update_list_detail", "waiting_update_gc_list", "ucache_check_alive_key"]:
            continue
        if i[:13] == "chat_sentinel":
            continue
        if i == "all_games":
            local_all_games = list(redis_store.smembers(i))
        elif i == "access_key":
            v = redis_store.hgetall(i)
            for k, ve in v.items():
                local_access_key[k] = ve
        elif i == "dun_secret":
            v = redis_store.hgetall(i)
            for k, ve in v.items():
                local_dun_secret[k] = json.loads(ve)
        elif i[:3] == "GC_":
            v = redis_store.hgetall(i)
            for k, ve in v.items():
                if k == "swich_shumei":
                    v[k] = ve
                else:
                    v[k] = json.loads(ve)
            local_gc_listname[i] = v
        else:
            v = redis_store.hgetall(i)
            data = pickle.loads(v["data"].encode("latin1")) if v.get("data") else ""
            v["data"] = data
            local_list_data[i] = v

    local_all_games = list(set(local_all_games))
    return local_all_games, local_gc_listname, local_list_data, local_access_key, local_dun_secret


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
    read_sql_all_game(sql_db, redis_store)
    read_sql_game_channel(sql_db, redis_store)
    read_sql_detail_data(sql_db, redis_store)


def read_sql_all_game(sql_db, redis_store):
    sql = """
                SELECT 
                    game_id
                FROM 
                    game
                WHERE
                    delete_time IS NULL
                """
    res = sql_db.select(sql)
    for i in res:
        redis_store.sadd("all_games", i[0])


def read_sql_game_channel(sql_db, redis_store):
    d = {}
    sql = """
            SELECT 
                list_game_channel.list_no AS list_no, list_game_channel.game_id AS game_id, 
                list_game_channel.channel_no AS channel_no, name_list.type AS list_type
            FROM 
                list_game_channel, name_list
            WHERE
                list_game_channel.list_no=name_list.no AND list_game_channel.delete_time IS NULL 
        """
    res = sql_db.select(sql, return_dict=True)
    for i in res:
        game_channel = "GC_{}_{}".format(i["game_id"], i["channel_no"])
        if not d.get(game_channel):
            d[game_channel] = {}
        if d[game_channel].get(i["list_type"]):
            d[game_channel][i["list_type"]].append(i["list_no"])
        else:
            d[game_channel][i["list_type"]] = [i["list_no"]]

    for k, v in d.items():
        for m, n in v.items():
            v[m] = json.dumps(n)
        redis_store.hset(k, mapping=v)
    return True


def read_sql_detail_data(sql_db, redis_store):
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
            }
        redis_store.hset(list_no, mapping=r)
