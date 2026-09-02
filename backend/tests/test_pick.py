"""加权选题测试：同答案字内，高赞题被选中概率更高"""
from collections import Counter


def test_weighted_favors_high_likes(client, db, make_riddle):
    """同一答案字两条题，高赞题应被显著更频繁选中"""
    popular = make_riddle(question="热门谜面", answer="明", likes=100, dislikes=0)
    unpopular = make_riddle(question="冷门谜面", answer="明", likes=0, dislikes=0)

    counts = Counter()
    for _ in range(120):
        res = client.get("/api/riddles/random", params={"grade": 1})
        counts[res.json()["id"]] += 1

    assert counts[popular.id] > counts[unpopular.id], \
        f"高赞题 {counts[popular.id]} 应多于低赞题 {counts[unpopular.id]}"


def test_low_quality_reduced_weight(client, db, make_riddle):
    """low_quality 题权重应被压低（同答案字对比）"""
    normal = make_riddle(question="正常谜面", answer="明", quality="normal")
    low = make_riddle(question="降权谜面", answer="明", quality="low_quality")

    counts = Counter()
    for _ in range(120):
        res = client.get("/api/riddles/random", params={"grade": 1})
        counts[res.json()["id"]] += 1

    assert counts[normal.id] > counts[low.id], \
        f"正常题 {counts[normal.id]} 应多于降权题 {counts[low.id]}"
