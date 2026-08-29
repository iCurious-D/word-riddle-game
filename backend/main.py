from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
import os
import random
from collections import defaultdict

from database import get_db
from models import Textbook, Riddle, CharacterInfo
# from generator import generate_riddle  # 导入生成器
from generator import generate_riddle_with_llm
from utils.char_utils import get_pinyin, get_structure, get_decompose
from utils.char_crawler import fetch_char_api

app = FastAPI()

# CORS 允许的前端域名，逗号分隔，默认 localhost
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/textbooks")
def get_textbooks(db: Session = Depends(get_db)):
    textbooks = db.query(Textbook).all()
    # 返回去重后的教材名称列表，以及年级列表供前端选择
    publishers = list(set([t.name for t in textbooks]))
    return {
        "publishers": publishers,  # 如 ["人教版", "苏教版"]
        "grades": [1,2,3,4,5,6]    # 简单返回可用年级
    }

@app.get("/api/riddles/random")
def get_random_riddle(
    grade: int = Query(0, description="年级，0 表示全部"),
    publisher: str = Query(None, description="教材版本，空表示全部"),
    term: int = Query(0, description="学期 1:上 2:下，0 表示全部"),
    use_auto: bool = Query(False, description="是否允许自动生成"),
    exclude_ids: str = Query(None, description="已做过的谜题 ID，逗号分隔"),
    db: Session = Depends(get_db)
):
    # 基础查询：按年级和教材筛选（0/空 表示不过滤）
    query = db.query(Riddle)
    if grade > 0:
        query = query.filter(Riddle.grade == grade)
    if publisher:
        query = query.join(Textbook).filter(Textbook.name == publisher)
        if term and term > 0:
            query = query.filter(Textbook.term == term)

    # 解析 exclude_ids："3,7,12" -> [3, 7, 12]
    exclude_list = []
    if exclude_ids:
        exclude_list = [int(x) for x in exclude_ids.split(",") if x.strip().isdigit()]

    # 辅助函数：加权随机选题（按答案字分组 + 评分权重）
    quality_map = {'normal': 1.0, 'low_quality': 0.2, 'flagged': 1.0}

    def pick_from_db():
        q = query.filter(Riddle.status == 'active')
        q = q.filter(Riddle.quality != 'rejected')
        if exclude_list:
            q = q.filter(Riddle.id.notin_(exclude_list))

        riddles = q.all()
        if not riddles:
            return None

        # 按答案字分组
        by_answer = defaultdict(list)
        for r in riddles:
            by_answer[r.answer].append(r)

        # 每组内按评分加权随机选一个候选
        candidates = []
        for answer, group in by_answer.items():
            weights = []
            for r in group:
                base = max(0.1, r.likes - r.dislikes + 1)
                mult = quality_map.get(r.quality, 1.0)
                weights.append(base * mult)
            total = sum(weights)
            pick = random.random() * total
            cumulative = 0
            selected = group[-1]
            for riddle, w in zip(group, weights):
                cumulative += w
                if pick <= cumulative:
                    selected = riddle
                    break
            candidates.append(selected)

        # 从各组候选中等概率选一个
        chosen = random.choice(candidates)
        return {
            "id": chosen.id,
            "question": chosen.question,
            "difficulty": chosen.difficulty,
            "source": chosen.source,
            "likes": chosen.likes,
            "dislikes": chosen.dislikes
        }

    # 辅助函数：调用 AI 生成新谜题并入库
    def generate_and_save():
        gen = generate_riddle_with_llm(grade, publisher, term)
        if not gen:
            return None

        textbook_id = None
        if publisher:
            textbook_query = db.query(Textbook).filter(
                Textbook.name == publisher,
                Textbook.grade == grade
            )
            if term:
                textbook_query = textbook_query.filter(Textbook.term == term)
            textbook = textbook_query.first()
            if textbook:
                textbook_id = textbook.id

        new_riddle = Riddle(
            question=gen["question"],
            answer=gen["answer"],
            difficulty=gen.get("difficulty", 1),
            grade=grade,
            source="ai",
            textbook_id=textbook_id
        )

        existing = db.query(Riddle).filter(
            Riddle.question == gen["question"],
            Riddle.answer == gen["answer"]
        ).first()

        if existing:
            new_riddle = existing
        else:
            db.add(new_riddle)
            db.commit()
            db.refresh(new_riddle)

        return {
            "id": new_riddle.id,
            "question": new_riddle.question,
            "difficulty": new_riddle.difficulty,
            "source": new_riddle.source
        }

    # 题库优先：先从 DB 取未见过的题
    db_result = pick_from_db()
    if db_result:
        return db_result

    # 题库做完了，尝试 AI 生成
    if use_auto:
        ai_result = generate_and_save()
        if ai_result:
            return ai_result
        return {"error": "AI 生成失败，请稍后重试"}

    return {"error": "题库已全部做完，可开启自动生成"}


@app.post("/api/riddles/check")
def check_answer(riddle_id: int = Query(...), answer: str = Query(...), db: Session = Depends(get_db)):
    riddle = db.query(Riddle).filter(Riddle.id == riddle_id).first()
    if not riddle:
        return {"error": "谜题不存在"}
    is_correct = (answer.strip() == riddle.answer.strip())
    return {
        "correct": is_correct,
        "answer": riddle.answer if not is_correct else None,
        "explanation": f"谜底是‘{riddle.answer}’" if not is_correct else "回答正确！"
    }


# ---------- 汉字信息工具函数 ----------

def get_or_fetch_char_info(char: str, db: Session) -> CharacterInfo | None:
    """查询汉字信息，DB 没有则在线查找并保存"""
    info = db.query(CharacterInfo).filter(CharacterInfo.char == char).first()
    if info:
        return info

    # 本地计算基础信息
    local = {
        "pinyin": get_pinyin(char),
        "structure": get_structure(char),
        "decompose": get_decompose(char),
    }

    # 在线获取部首、释义、笔画
    api_data = fetch_char_api(char)

    info = CharacterInfo(
        char=char,
        pinyin=(api_data.get("pinyin") if api_data else None) or local["pinyin"],
        radical=api_data.get("radical") if api_data else None,
        strokes=api_data.get("strokes") if api_data else None,
        structure=local["structure"],
        meaning=api_data.get("meaning") if api_data else None,
        decompose=local["decompose"],
    )
    try:
        db.add(info)
        db.commit()
        db.refresh(info)
    except Exception:
        db.rollback()
    return info


# ---------- 提示接口 ----------

@app.get("/api/riddles/hint")
def get_hint(riddle_id: int = Query(...), level: int = Query(1, ge=1, le=3), db: Session = Depends(get_db)):
    """三级提示：1-结构类型 2-部首 3-拼音+释义"""
    riddle = db.query(Riddle).filter(Riddle.id == riddle_id).first()
    if not riddle:
        return {"error": "谜题不存在"}

    answer = riddle.answer.strip()
    char_info = get_or_fetch_char_info(answer, db)

    if level == 1:
        hint_text = char_info.structure if char_info and char_info.structure else "暂无结构信息"
    elif level == 2:
        if char_info and char_info.radical:
            hint_text = f"部首是‘{char_info.radical}’"
        else:
            hint_text = "暂无部首信息"
    elif level == 3:
        pinyin = char_info.pinyin if char_info and char_info.pinyin else "???"
        meaning = char_info.meaning if char_info and char_info.meaning else "暂无释义"
        hint_text = f"{pinyin}，{meaning}"
    else:
        return {"error": "无效的提示级别"}

    return {"level": level, "hint": hint_text}


# ---------- 汉字详情接口 ----------

@app.get("/api/char/info")
def get_char_info(char: str = Query(..., description="单个汉字"), db: Session = Depends(get_db)):
    """获取汉字详细信息，用于答后展示"""
    char = char.strip()
    if len(char) != 1:
        return {"error": "请输入单个汉字"}

    info = get_or_fetch_char_info(char, db)
    if not info:
        return {"error": "无法获取汉字信息"}

    return {
        "char": char,
        "pinyin": info.pinyin,
        "radical": info.radical,
        "strokes": info.strokes,
        "structure": info.structure,
        "meaning": info.meaning,
        "decompose": info.decompose,
    }


# ---------- 评价系统 ----------

@app.post("/api/riddles/vote")
def vote_riddle(
    riddle_id: int = Query(..., description="谜题 ID"),
    vote: str = Query(..., description="up 或 down"),
    db: Session = Depends(get_db)
):
    """对谜题投票（赞/踩）"""
    riddle = db.query(Riddle).filter(Riddle.id == riddle_id).first()
    if not riddle:
        return {"error": "谜题不存在"}

    if vote == "up":
        riddle.likes += 1
    elif vote == "down":
        riddle.dislikes += 1
        # 自动标记：差评达阈值且 quality 还是 normal
        total_votes = riddle.likes + riddle.dislikes
        if (riddle.dislikes >= 3 and
            total_votes > 0 and
            riddle.dislikes / total_votes > 0.5 and
            riddle.quality == 'normal'):
            riddle.quality = 'flagged'
    else:
        return {"error": "无效的投票类型"}

    db.commit()
    return {"likes": riddle.likes, "dislikes": riddle.dislikes}


# ---------- 用户上传字谜 ----------

@app.post("/api/riddles/submit")
def submit_riddle(
    question: str = Query(..., description="谜面"),
    answer: str = Query(..., description="谜底（单个汉字）"),
    grade: int = Query(..., ge=1, le=6, description="适用年级 1-6"),
    difficulty: int = Query(2, ge=1, le=3, description="难度 1-3"),
    submitter: str = Query(None, description="提交者昵称"),
    db: Session = Depends(get_db)
):
    """用户提交自创字谜"""
    answer = answer.strip()
    if len(answer) != 1:
        return {"error": "谜底必须是单个汉字"}

    # 查重
    existing = db.query(Riddle).filter(
        Riddle.question == question.strip(),
        Riddle.answer == answer
    ).first()
    if existing:
        return {"error": "该谜题已存在"}

    new_riddle = Riddle(
        question=question.strip(),
        answer=answer,
        grade=grade,
        difficulty=difficulty,
        source="user",
        status="pending",
        submitter=submitter.strip() if submitter else None
    )
    db.add(new_riddle)
    db.commit()
    db.refresh(new_riddle)
    return {"success": True, "id": new_riddle.id, "message": "提交成功，审核通过后将参与出题"}


# ---------- 管理员审核 ----------

@app.get("/api/admin/riddles")
def list_admin_riddles(
    filter: str = Query('pending', description="筛选: pending/flagged/low_quality/rejected/active"),
    db: Session = Depends(get_db)
):
    """列出谜题（按状态筛选）"""
    q = db.query(Riddle)
    if filter == 'pending':
        q = q.filter(Riddle.status == 'pending')
    elif filter == 'flagged':
        q = q.filter(Riddle.quality == 'flagged')
    elif filter in ('low_quality', 'rejected'):
        q = q.filter(Riddle.quality == filter)
    elif filter == 'active':
        q = q.filter(Riddle.status == 'active', Riddle.quality == 'normal')
    else:
        return {"error": "无效的筛选条件"}

    riddles = q.order_by(Riddle.id.desc()).limit(100).all()
    return [{
        "id": r.id, "question": r.question, "answer": r.answer,
        "grade": r.grade, "difficulty": r.difficulty,
        "likes": r.likes, "dislikes": r.dislikes,
        "quality": r.quality, "status": r.status,
        "source": r.source, "submitter": r.submitter
    } for r in riddles]


@app.post("/api/admin/riddles/{riddle_id}/review")
def review_riddle(
    riddle_id: int,
    action: str = Query(..., description="操作: approve/reject/lower/restore"),
    db: Session = Depends(get_db)
):
    """管理员审核谜题"""
    riddle = db.query(Riddle).filter(Riddle.id == riddle_id).first()
    if not riddle:
        return {"error": "谜题不存在"}

    if action == 'approve':
        riddle.status = 'active'
        if riddle.quality == 'flagged':
            riddle.quality = 'normal'
    elif action == 'reject':
        riddle.status = 'rejected'
        riddle.quality = 'rejected'
    elif action == 'lower':
        riddle.quality = 'low_quality'
    elif action == 'restore':
        riddle.quality = 'normal'
        riddle.status = 'active'
    else:
        return {"error": "无效的操作"}

    db.commit()
    return {"success": True, "quality": riddle.quality, "status": riddle.status}