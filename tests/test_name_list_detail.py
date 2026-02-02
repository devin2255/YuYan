def test_name_list_and_detail(client):
    client.post("/dun/game", json={"game_id": "4001", "name": "Game4001", "username": "tester"})
    client.post("/dun/channel", json={"no": "ch4001", "name": "Channel4001", "memo": "", "username": "tester"})

    create_payload = {
        "name": "List4001",
        "type": 1,
        "match_rule": 1,
        "match_type": 1,
        "suggest": 1,
        "risk_type": 300,
        "status": 1,
        "language": "all",
        "channel": "ch4001",
        "game_id": "4001",
        "username": "tester",
    }
    resp = client.post("/dun/name_list", json=create_payload)
    assert resp.status_code == 200

    lists = client.get("/dun/name_list").json()
    list_id = lists[0]["id"]
    list_no = lists[0]["no"]

    update_payload = dict(create_payload)
    update_payload["name"] = "List4001v2"
    resp = client.put(f"/dun/name_list/{list_id}", json=update_payload)
    assert resp.status_code == 200

    resp = client.post(f"/dun/name_list/swich/{list_id}", json={"status": 0, "username": "tester"})
    assert resp.status_code == 200

    resp = client.post(
        "/dun/list_detail",
        json={"list_no": list_no, "text": "badword", "username": "tester", "memo": ""},
    )
    assert resp.status_code == 200

    from yuyan.app.models.list_detail import ListDetail

    db = client.app.state.SessionLocal()
    detail = db.query(ListDetail).filter(ListDetail.text == "badword").first()
    detail_id = detail.id
    db.close()

    resp = client.put(
        f"/dun/list_detail/{detail_id}",
        json={"text": "badword2", "username": "tester", "memo": ""},
    )
    assert resp.status_code == 200

    resp = client.delete(
        "/dun/list_detail/del_text",
        json={"list_name": "List4001v2", "text": "badword2", "username": "tester"},
    )
    assert resp.status_code == 200

    resp = client.post(
        "/dun/list_detail/batch",
        json={"list_no": list_no, "data": ["alpha", "beta"], "username": "tester"},
    )
    assert resp.status_code == 200

    db = client.app.state.SessionLocal()
    detail_ids = [item.id for item in db.query(ListDetail).filter(ListDetail.text == "alpha").all()]
    db.close()

    resp = client.delete("/dun/list_detail/batch", json={"ids": detail_ids, "username": "tester"})
    assert resp.status_code == 200

    resp = client.delete(f"/dun/name_list/{list_id}")
    assert resp.status_code == 200
