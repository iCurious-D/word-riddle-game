"""管理后台测试：密码验证 / 鉴权 / 审核状态机"""


def _token(client):
    res = client.post("/api/admin/verify", params={"password": "testpass"})
    return res.json()["token"]


# ---------- 密码验证 ----------

def test_verify_wrong_password(client):
    res = client.post("/api/admin/verify", params={"password": "wrong"})
    assert res.json()["error"] == "密码错误"


def test_verify_correct_password(client):
    res = client.post("/api/admin/verify", params={"password": "testpass"})
    assert "token" in res.json()


# ---------- 鉴权 ----------

def test_admin_list_requires_token(client, db, make_riddle):
    make_riddle()
    res = client.get("/api/admin/riddles", params={"filter": "active"})
    assert res.status_code == 401


def test_admin_list_with_token(client, db, make_riddle):
    make_riddle()
    res = client.get("/api/admin/riddles",
                     params={"filter": "active"},
                     headers={"Authorization": _token(client)})
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_review_requires_token(client, db, make_riddle):
    r = make_riddle()
    res = client.post(f"/api/admin/riddles/{r.id}/review", params={"action": "approve"})
    assert res.status_code == 401


# ---------- 审核状态机 ----------

def test_review_approve_pending(client, db, make_riddle):
    r = make_riddle(status="pending")
    client.post(f"/api/admin/riddles/{r.id}/review",
                params={"action": "approve"},
                headers={"Authorization": _token(client)})
    db.refresh(r)
    assert r.status == "active"


def test_review_reject(client, db, make_riddle):
    r = make_riddle()
    client.post(f"/api/admin/riddles/{r.id}/review",
                params={"action": "reject"},
                headers={"Authorization": _token(client)})
    db.refresh(r)
    assert r.status == "rejected"
    assert r.quality == "rejected"


def test_review_lower(client, db, make_riddle):
    r = make_riddle()
    client.post(f"/api/admin/riddles/{r.id}/review",
                params={"action": "lower"},
                headers={"Authorization": _token(client)})
    db.refresh(r)
    assert r.quality == "low_quality"


def test_review_restore_flagged(client, db, make_riddle):
    r = make_riddle(quality="flagged")
    client.post(f"/api/admin/riddles/{r.id}/review",
                params={"action": "restore"},
                headers={"Authorization": _token(client)})
    db.refresh(r)
    assert r.quality == "normal"
    assert r.status == "active"


def test_rejected_not_served(client, db, make_riddle):
    """被下架的题不应再出给用户"""
    r = make_riddle(quality="rejected")
    res = client.get("/api/riddles/random", params={"grade": 1})
    assert res.json().get("error")  # 唯一题已下架 → 无题可出
