import json


def test_text_filter_pass(client, monkeypatch):
    from yuyan.app.services import text_service

    monkeypatch.setattr(text_service, "all_filter", lambda *args, **kwargs: args[1])

    payload = {
        "accessKey": "test_key",
        "ugcSource": "chat",
        "data": json.dumps(
            {
                "timestamp": 1,
                "tokenId": "t1",
                "nickname": "nick",
                "text": "hello",
                "serverId": "s1",
                "accountId": "a1",
                "gameId": "1001",
                "roleId": "r1",
                "vipLevel": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
            }
        ),
    }
    resp = client.post("/dun/chatmsg.anti", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "PASS"
    assert data["requestId"]


def test_text_filter_reject(client, monkeypatch):
    from yuyan.app.services import text_service

    def fake_all_filter(chat_msg, resp, core_app, language_pred):
        resp["riskLevel"] = "REJECT"
        resp["detail"] = {"hit": True}
        return resp

    monkeypatch.setattr(text_service, "all_filter", fake_all_filter)

    payload = {
        "accessKey": "test_key",
        "ugcSource": "chat",
        "data": json.dumps(
            {
                "timestamp": 1,
                "tokenId": "t1",
                "nickname": "nick",
                "text": "spam",
                "serverId": "s1",
                "accountId": "a1",
                "gameId": "1001",
                "roleId": "r1",
                "vipLevel": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
            }
        ),
    }
    resp = client.post("/dun/chatmsg.anti", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "REJECT"
    assert data["requestId"]


def test_image_filter_pass(client):
    payload = {
        "accessKey": "test_key",
        "data": json.dumps(
            {
                "timestamp": 1,
                "img": "base64",
                "serverId": "s1",
                "accountId": "a1",
                "gameId": "1001",
                "roleId": "r1",
                "vipLevel": "1",
                "level": "1",
                "ip": "127.0.0.1",
                "channel": "c1",
                "targetId": "",
                "organizationId": "",
                "teamId": "",
                "sceneId": "",
            }
        ),
    }
    resp = client.post("/dun/imgfilter.anti", json=payload)
    data = resp.json()
    assert resp.status_code == 200
    assert data["riskLevel"] == "PASS"
