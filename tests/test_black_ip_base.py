import json


def test_black_ip_crud(client):
    resp = client.get("/blacklisted-ips")
    assert resp.status_code == 200

    resp = client.post("/blacklisted-ips", json={"ip": "2.2.2.2", "username": "tester"})
    assert resp.status_code == 200

    resp = client.delete("/blacklisted-ips/2.2.2.2")
    assert resp.status_code == 200


def test_base_endpoints(client, fake_redis, monkeypatch):
    from app.api.v1 import base as base_module

    monkeypatch.setattr(base_module, "sql_data_to_redis", lambda *args, **kwargs: None)

    fake_redis.hset("chat_sentinel_ip", "RULE1", json.dumps({"1001": ["1.1.1.1"]}))
    fake_redis.hset("chat_sentinel_account_id", "ARULE", json.dumps({"1001": ["acc1"]}))

    client.post("/apps", json={"app_id": "5001", "name": "App5001", "username": "tester"})

    get_paths = [
        "/cache/apps",
        "/cache/app-channels",
        "/cache/list-data",
        "/cache/redis/apps",
        "/cache/redis/pending-list-details",
        "/cache/redis/pending-app-channels",
        "/cache/redis/app-channels",
        "/cache/redis/list-data",
        "/cache/redis/chat-sentinel/accounts",
        "/cache/redis/chat-sentinel/ips",
    ]
    for path in get_paths:
        resp = client.get(path)
        assert resp.status_code == 200

    post_paths = [
        "/cache/refresh",
        "/cache/redis/import",
        "/cache/apps/refresh-from-redis",
        "/cache/app-channels/refresh-from-redis",
        "/cache/list-data/refresh-from-redis",
        "/cache/apps/refresh-from-db",
        "/cache/redis/pending-app-channels/reset",
        "/cache/redis/pending-list-details/reset",
    ]
    for path in post_paths:
        resp = client.post(path)
        assert resp.status_code == 200

    resp = client.post("/cache/redis/chat-sentinel/ips/reset", params={"rule": "RULE1"})
    assert resp.status_code == 200

    resp = client.post("/cache/redis/chat-sentinel/accounts/reset", params={"rule": "ARULE"})
    assert resp.status_code == 200
