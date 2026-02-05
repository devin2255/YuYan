def test_name_list_and_detail(client):
    client.post("/apps", json={"app_id": "4001", "name": "App4001", "username": "tester"})
    client.post("/channels", json={"name": "Channel4001", "memo": "", "username": "tester"})
    channels = client.get("/channels").json()["data"]
    channel_id = next(item["id"] for item in channels if item["name"] == "Channel4001")

    create_payload = {
        "name": "List4001",
        "type": 1,
        "match_rule": 1,
        "match_type": 1,
        "suggest": 1,
        "risk_type": 300,
        "status": 1,
        "language_scope": "ALL",
        "language_codes": [],
        "scope": "APP_CHANNEL",
        "channel_ids": [channel_id],
        "app_ids": ["4001"],
        "username": "tester",
    }
    resp = client.post("/name-lists", json=create_payload)
    assert resp.status_code == 200

    lists = client.get("/name-lists").json()
    list_id = lists[0]["id"]
    list_no = lists[0]["no"]

    update_payload = dict(create_payload)
    update_payload["name"] = "List4001v2"
    resp = client.put(f"/name-lists/{list_id}", json=update_payload)
    assert resp.status_code == 200

    resp = client.patch(f"/name-lists/{list_id}/status", json={"status": 0, "username": "tester"})
    assert resp.status_code == 200

    resp = client.post(
        "/list-details",
        json={"list_no": list_no, "text": "badword", "username": "tester", "memo": ""},
    )
    assert resp.status_code == 200

    from app.models.list_detail import ListDetail

    db = client.app.state.SessionLocal()
    detail = db.query(ListDetail).filter(ListDetail.text == "badword").first()
    detail_id = detail.id
    db.close()

    resp = client.put(
        f"/list-details/{detail_id}",
        json={"text": "badword2", "username": "tester", "memo": ""},
    )
    assert resp.status_code == 200

    resp = client.request(
        "DELETE",
        "/list-details/by-text",
        json={"list_name": "List4001v2", "text": "badword2", "username": "tester"},
    )
    assert resp.status_code == 200

    resp = client.post(
        "/list-details/batch",
        json={"list_no": list_no, "data": ["alpha", "beta"], "username": "tester"},
    )
    assert resp.status_code == 200

    db = client.app.state.SessionLocal()
    detail_ids = [item.id for item in db.query(ListDetail).filter(ListDetail.text == "alpha").all()]
    db.close()

    resp = client.request("DELETE", "/list-details/batch", json={"ids": detail_ids, "username": "tester"})
    assert resp.status_code == 200

    resp = client.delete(f"/name-lists/{list_id}")
    assert resp.status_code == 200
