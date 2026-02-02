def test_game_crud(client):
    create_payload = {"game_id": "2001", "name": "Game2001", "username": "tester"}
    resp = client.post("/dun/game", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/dun/game")
    assert resp.status_code == 200
    games = resp.json()["data"]
    assert any(item["game_id"] == "2001" for item in games)

    resp = client.get("/dun/game/2001")
    assert resp.status_code == 200
    assert resp.json()["data"]["game_id"] == "2001"

    update_payload = {"name": "Game2001v2", "username": "tester"}
    resp = client.put("/dun/game/2001", json=update_payload)
    assert resp.status_code == 200

    resp = client.delete("/dun/game/2001")
    assert resp.status_code == 200


def test_channel_crud(client):
    create_payload = {"no": "ch1", "name": "Channel1", "memo": "memo", "username": "tester"}
    resp = client.post("/dun/channel", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/dun/channel")
    assert resp.status_code == 200
    channels = resp.json()["data"]
    assert any(item["no"] == "ch1" for item in channels)

    resp = client.get("/dun/channel/ch1")
    assert resp.status_code == 200
    assert resp.json()["data"]["no"] == "ch1"

    update_payload = {"name": "Channel1v2", "memo": "memo"}
    resp = client.put("/dun/channel/ch1", json=update_payload)
    assert resp.status_code == 200

    resp = client.delete("/dun/channel/ch1")
    assert resp.status_code == 200
