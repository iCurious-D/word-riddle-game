from database import engine, SessionLocal, Base
from models import Textbook, Riddle

def init_db():
    Base.metadata.create_all(bind=engine)

def seed():
    db = SessionLocal()
    # 检查是否已经有数据，避免重复插入
    if db.query(Textbook).count() > 0:
        print("数据库已有数据，跳过种子数据插入。")
        db.close()
        return

    # 教材版本
    textbooks = [
        Textbook(name="人教版", grade=1, term=1),
        Textbook(name="人教版", grade=1, term=2),
        Textbook(name="人教版", grade=2, term=1),
        Textbook(name="人教版", grade=2, term=2),
        Textbook(name="苏教版", grade=1, term=1),
        Textbook(name="苏教版", grade=1, term=2),
        Textbook(name="苏教版", grade=2, term=1),
        Textbook(name="苏教版", grade=2, term=2),
        # 可继续添加更多年级...
    ]
    db.add_all(textbooks)
    db.flush()  # 获取 textbook id

    # 经典字谜，关联到教材和年级（这里简单按年级分配，与教材具体版本无关）
    riddles = [
        Riddle(question="一口咬掉牛尾巴", answer="告", difficulty=1, textbook_id=1, grade=1),
        Riddle(question="太阳落在月亮旁", answer="明", difficulty=1, textbook_id=1, grade=1),
        Riddle(question="左边绿，右边红，左右相遇起凉风", answer="秋", difficulty=2, textbook_id=3, grade=2),
        Riddle(question="一家十一口", answer="吉", difficulty=1, textbook_id=3, grade=2),
        Riddle(question="一点一横长，一撇到南洋", answer="广", difficulty=2, textbook_id=2, grade=1),
        Riddle(question="七十二小时", answer="晶", difficulty=3, textbook_id=4, grade=2),
        Riddle(question="需要一半，留下一半", answer="雷", difficulty=2, textbook_id=4, grade=2),
        Riddle(question="一百减一", answer="白", difficulty=1, textbook_id=2, grade=1),
        Riddle(question="一月一日非今天", answer="明", difficulty=2, textbook_id=3, grade=2),
        Riddle(question="山上还有山", answer="出", difficulty=1, textbook_id=1, grade=1),
    ]
    db.add_all(riddles)
    db.commit()
    db.close()
    print("种子数据插入完成。")


if __name__ == "__main__":
    init_db()
    seed()