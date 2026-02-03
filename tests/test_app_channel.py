def test_app_crud(client):
    create_payload = {"app_id": "2001", "name": "App2001", "username": "tester"}
    resp = client.post("/apps", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/apps")
    assert resp.status_code == 200
    apps = resp.json()["data"]
    assert any(item["app_id"] == "2001" for item in apps)

    resp = client.get("/apps/2001")
    assert resp.status_code == 200
    assert resp.json()["data"]["app_id"] == "2001"

    update_payload = {"name": "App2001v2", "username": "tester"}
    resp = client.put("/apps/2001", json=update_payload)
    assert resp.status_code == 200

    resp = client.delete("/apps/2001")
    assert resp.status_code == 200


def test_channel_crud(client):
    create_payload = {"name": "Channel1", "memo": "memo", "username": "tester"}
    resp = client.post("/channels", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/channels")
    assert resp.status_code == 200
    channels = resp.json()["data"]
    channel_id = next(item["id"] for item in channels if item["name"] == "Channel1")

    resp = client.get(f"/channels/{channel_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["name"] == "Channel1"

    update_payload = {"name": "Channel1v2", "memo": "memo"}
    resp = client.put(f"/channels/{channel_id}", json=update_payload)
    assert resp.status_code == 200

    resp = client.delete(f"/channels/{channel_id}")
    assert resp.status_code == 200
