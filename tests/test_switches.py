def test_switches_and_threshold(client):
    client.post("/apps", json={"app_id": "3001", "name": "App3001", "username": "tester"})

    resp = client.post("/ai-switches", json={"switch": "ON", "app_id": "3001", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/ai-switches")
    assert resp.status_code == 200
    ai_id = resp.json()[0]["id"]
    resp = client.put(f"/ai-switches/{ai_id}", json={"switch": "OFF", "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/ai-switches/{ai_id}")
    assert resp.status_code == 200

    resp = client.post("/ac-switches", json={"switch": "ON", "app_id": "3001", "channel": "all", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/ac-switches")
    assert resp.status_code == 200
    ac_id = resp.json()[0]["id"]
    resp = client.put(f"/ac-switches/{ac_id}", json={"switch": "OFF", "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/ac-switches/{ac_id}")
    assert resp.status_code == 200

    resp = client.post("/model-thresholds", json={"threshold": 0.9, "app_id": "3001", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/model-thresholds")
    assert resp.status_code == 200
    mt_id = resp.json()[0]["id"]
    resp = client.put(f"/model-thresholds/{mt_id}", json={"threshold": 0.8, "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/model-thresholds/{mt_id}")
    assert resp.status_code == 200
