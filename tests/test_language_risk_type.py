def test_language_crud(client):
    create_payload = {"name": "中文", "abbrev": "zh", "username": "tester"}
    resp = client.post("/dun/language", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/dun/language")
    assert resp.status_code == 200
    languages = resp.json()["data"]
    lang_id = next(item["id"] for item in languages if item["abbrev"] == "zh")

    resp = client.get(f"/dun/language/{lang_id}")
    assert resp.status_code == 200

    update_payload = {"name": "中文简体", "abbrev": "zh", "username": "tester"}
    resp = client.put(f"/dun/language/{lang_id}", json=update_payload)
    assert resp.status_code == 200

    resp = client.delete(f"/dun/language/{lang_id}", json={"username": "tester"})
    assert resp.status_code == 200


def test_risk_type_create(client):
    create_payload = {"no": 999, "desc": "测试风险", "abbrev": "TEST", "username": "tester"}
    resp = client.post("/dun/risk_type", json=create_payload)
    assert resp.status_code == 200

    resp = client.get("/dun/risk_type")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert any(item["no"] == 999 for item in data)
