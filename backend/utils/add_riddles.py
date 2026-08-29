# add_riddles.py
from database import SessionLocal
from models import Riddle, Textbook

db = SessionLocal()
new_riddles = [
    Riddle(question="一口咬掉牛尾巴", answer="告", difficulty=1, textbook_id=1, grade=1),
    # ... 继续添加
]
db.add_all(new_riddles)
db.commit()
db.close()
