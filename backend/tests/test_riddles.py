"""核心玩法测试：答案校验 / 投票 / 上传 / 出题"""


# ---------- 答案校验 ----------

def test_check_answer_correct(client, db, make_riddle):
    r = make_riddle()
    res = client.post("/api/riddles/check", params={"riddle_id": r.id, "answer": "告"})
    assert res.json()["correct"] is True


def test_check_answer_wrong(client, db, make_riddle):
    r = make_riddle()
    res = client.post("/api/riddles/check", params={"riddle_id": r.id, "answer": "日"})
    data = res.json()
    assert data["correct"] is False
    assert data["answer"] == "告"  # 答错时返回正确答案


def test_check_answer_strips_spaces(client, db, make_riddle):
    r = make_riddle()
    res = client.post("/api/riddles/check", params={"riddle_id": r.id, "answer": " 告 "})
    assert res.json()["correct"] is True


# ---------- 投票 ----------

def test_vote_up(client, db, make_riddle):
    r = make_riddle()
    res = client.post("/api/riddles/vote", params={"riddle_id": r.id, "vote": "up"})
    assert res.json()["likes"] == 1


def test_vote_down(client, db, make_riddle):
    r = make_riddle()
    res = client.post("/api/riddles/vote", params={"riddle_id": r.id, "vote": "down"})
    assert res.json()["dislikes"] == 1


def test_vote_auto_flag(client, db, make_riddle):
    """踩满 3 且占比过半 → quality 自动变 flagged"""
    r = make_riddle()
    for _ in range(3):
        client.post("/api/riddles/vote", params={"riddle_id": r.id, "vote": "down"})
    db.refresh(r)
    assert r.quality == "flagged"


def test_vote_no_flag_below_threshold(client, db, make_riddle):
    """踩 2 次未达阈值 → 仍为 normal"""
    r = make_riddle()
    for _ in range(2):
        client.post("/api/riddles/vote", params={"riddle_id": r.id, "vote": "down"})
    db.refresh(r)
    assert r.quality == "normal"


# ---------- 上传 ----------

def test_submit_ok(client):
    res = client.post("/api/riddles/submit", json={
        "question": "太阳和月亮在一起", "answer": "明",
        "grade": 1, "difficulty": 2, "submitter": "测试",
    })
    data = res.json()
    assert data["success"] is True
    assert data["id"] >= 1


def test_submit_pending_status(client, db):
    client.post("/api/riddles/submit", json={
        "question": "太阳和月亮在一起", "answer": "明", "grade": 1,
    })
    from models import Riddle
    r = db.query(Riddle).first()
    assert r.status == "pending"  # 上传默认待审核


def test_submit_invalid_answer(client):
    res = client.post("/api/riddles/submit", json={
        "question": "谜面", "answer": "两个字", "grade": 1,
    })
    assert "error" in res.json()


def test_submit_duplicate(client):
    payload = {"question": "太阳和月亮在一起", "answer": "明", "grade": 1}
    client.post("/api/riddles/submit", json=payload)
    res = client.post("/api/riddles/submit", json=payload)
    assert res.json()["error"] == "该谜题已存在"


# ---------- 出题 ----------

def test_random_returns_riddle(client, db, make_riddle):
    make_riddle()
    res = client.get("/api/riddles/random", params={"grade": 1})
    data = res.json()
    assert "question" in data
    assert "answer" not in data  # 安全：不泄露答案


def test_random_respects_grade(client, db, make_riddle):
    make_riddle(grade=3, question="三年级的题")
    res = client.get("/api/riddles/random", params={"grade": 1})
    assert res.json().get("error")  # 一年级无题 → 返回 error


def test_random_excludes_seen(client, db, make_riddle):
    r = make_riddle()
    res = client.get("/api/riddles/random", params={"grade": 1, "exclude_ids": str(r.id)})
    assert res.json().get("error")  # 唯一题被排除 → 无题可出
