def test_switches_and_threshold(client):
    client.post("/dun/game", json={"game_id": "3001", "name": "Game3001", "username": "tester"})

    resp = client.post("/dun/ai_switch", json={"switch": "ON", "game_id": "3001", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/dun/ai_switch")
    assert resp.status_code == 200
    ai_id = resp.json()[0]["id"]
    resp = client.put(f"/dun/ai_switch/{ai_id}", json={"switch": "OFF", "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/dun/ai_switch/{ai_id}")
    assert resp.status_code == 200

    resp = client.post("/dun/ac_switch", json={"switch": "ON", "game_id": "3001", "channel": "all", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/dun/ac_switch")
    assert resp.status_code == 200
    ac_id = resp.json()[0]["id"]
    resp = client.put(f"/dun/ac_switch/{ac_id}", json={"switch": "OFF", "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/dun/ac_switch/{ac_id}")
    assert resp.status_code == 200

    resp = client.post("/dun/model_threshold", json={"threshold": 0.9, "game_id": "3001", "username": "tester"})
    assert resp.status_code == 200
    resp = client.get("/dun/model_threshold")
    assert resp.status_code == 200
    mt_id = resp.json()[0]["id"]
    resp = client.put(f"/dun/model_threshold/{mt_id}", json={"threshold": 0.8, "username": "tester"})
    assert resp.status_code == 200
    resp = client.delete(f"/dun/model_threshold/{mt_id}")
    assert resp.status_code == 200
