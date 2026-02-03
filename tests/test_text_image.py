import json


def test_text_filter_pass(client, monkeypatch):
    from app.services import text_service

    monkeypatch.setattr(text_service, "all_filter", lambda *args, **kwargs: args[1])

    payload = {
        "access_key": "test_key",
        "ugc_source": "chat",
        "data": json.dumps(
            {
                "timestamp": 1,
                "token_id": "t1",
                "nickname": "nick",
                "text": "hello",
                "server_id": "s1",
                "account_id": "a1",
                "app_id": "1001",
                "role_id": "r1",
                "vip_level": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
            }
        ),
    }
    resp = client.post("/moderation/text", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "PASS"
    assert data["requestId"]


def test_text_filter_reject(client, monkeypatch):
    from app.services import text_service

    def fake_all_filter(chat_msg, resp, core_app, language_pred):
        resp["riskLevel"] = "REJECT"
        resp["detail"] = {"hit": True}
        return resp

    monkeypatch.setattr(text_service, "all_filter", fake_all_filter)

    payload = {
        "access_key": "test_key",
        "ugc_source": "chat",
        "data": json.dumps(
            {
                "timestamp": 1,
                "token_id": "t1",
                "nickname": "nick",
                "text": "spam",
                "server_id": "s1",
                "account_id": "a1",
                "app_id": "1001",
                "role_id": "r1",
                "vip_level": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
            }
        ),
    }
    resp = client.post("/moderation/text", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "REJECT"
    assert data["requestId"]


def test_image_filter_pass(client):
    payload = {
        "access_key": "test_key",
        "data": json.dumps(
            {
                "timestamp": 1,
                "img": "base64",
                "server_id": "s1",
                "account_id": "a1",
                "app_id": "1001",
                "role_id": "r1",
                "vip_level": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
                "target_id": "",
                "organization_id": "",
                "team_id": "",
                "scene_id": "",
            }
        ),
    }
    resp = client.post("/moderation/images", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "PASS"
