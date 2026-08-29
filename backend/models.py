from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class CharacterInfo(Base):
    """汉字详细信息表，用于提示功能和答后展示"""
    __tablename__ = "character_info"

    char = Column(String(1), primary_key=True)          # 汉字，如 "明"
    pinyin = Column(String(20), nullable=True)           # 拼音，如 "míng"
    radical = Column(String(10), nullable=True)          # 部首，如 "日"
    strokes = Column(Integer, nullable=True)             # 笔画数，如 8
    structure = Column(String(10), nullable=True)        # 结构，如 "左右"
    meaning = Column(String(100), nullable=True)         # 释义，如 "亮，清楚"
    decompose = Column(String(50), nullable=True)        # 拆字，如 "日+月"
    # todo: 添加用字例句或者包含该字的名言名句，如 "明月松间照"

class Textbook(Base):
    __tablename__ = "textbooks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, comment="教材名称，如人教版")
    grade = Column(Integer, comment="年级 1-6")
    term = Column(Integer, comment="学期 1:上 2:下")

    riddles = relationship("Riddle", back_populates="textbook")

class Riddle(Base):
    __tablename__ = "riddles"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, comment="谜面")
    answer = Column(String, comment="谜底")
    difficulty = Column(Integer, default=1, comment="难度 1-3")
    textbook_id = Column(Integer, ForeignKey("textbooks.id"), nullable=True)
    grade = Column(Integer, comment="适用年级")
    source = Column(String, default="manual")  # manual / auto / user
    created_at = Column(DateTime, default=datetime.utcnow)

    # 评价系统
    likes = Column(Integer, default=0, comment="赞数")
    dislikes = Column(Integer, default=0, comment="踩数")
    quality = Column(String(10), default='normal', comment="质量标记: normal/low_quality/rejected/flagged")
    status = Column(String(10), default='active', comment="状态: active/pending")
    submitter = Column(String(50), nullable=True, comment="上传者昵称")

    textbook = relationship("Textbook", back_populates="riddles")