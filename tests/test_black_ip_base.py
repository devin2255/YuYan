import json


def test_black_ip_crud(client):
    resp = client.get("/dun/black_client_ip")
    assert resp.status_code == 200

    resp = client.post("/dun/black_client_ip", json={"ip": "2.2.2.2", "username": "tester"})
    assert resp.status_code == 200

    resp = client.delete("/dun/black_client_ip/delete", json={"ip": "2.2.2.2", "username": "tester"})
    assert resp.status_code == 200


def test_base_endpoints(client, fake_redis, monkeypatch):
    from yuyan.app.api.v1 import base as base_module

    monkeypatch.setattr(base_module, "sql_data_to_redis", lambda *args, **kwargs: None)

    fake_redis.hset("chat_sentinel_ip", "RULE1", json.dumps({"1001": ["1.1.1.1"]}))
    fake_redis.hset("chat_sentinel_account_id", "ARULE", json.dumps({"1001": ["acc1"]}))

    client.post("/dun/game", json={"game_id": "5001", "name": "Game5001", "username": "tester"})

    paths = [
        "/dun/base/local_cache_games",
        "/dun/base/local_cache_gc",
        "/dun/base/local_cache_data",
        "/dun/base/update_cache",
        "/dun/base/sql2redis",
        "/dun/base/redis/update_local_games",
        "/dun/base/redis/games",
        "/dun/base/redis/update_local_gc",
        "/dun/base/redis/waiting_update_list_detail",
        "/dun/base/redis/waiting_update_gc_list",
        "/dun/base/redis/game_channel",
        "/dun/base/redis/update_local_detail",
        "/dun/base/redis/list_detail",
        "/dun/base/mysql/update_local_games",
        "/dun/base/redis/waiting_update_gc_list/reset",
        "/dun/base/redis/waiting_update_list_detail/reset",
        "/dun/base/redis/chat_sentinel/account",
        "/dun/base/redis/chat_sentinel/ip",
        "/dun/base/redis/dun_secret",
    ]
    for path in paths:
        resp = client.get(path)
        assert resp.status_code == 200

    resp = client.get("/dun/base/redis/chat_sentinel/ip/reset", params={"rule": "RULE1"})
    assert resp.status_code == 200

    resp = client.get("/dun/base/redis/chat_sentinel/account/reset", params={"rule": "ARULE"})
    assert resp.status_code == 200
