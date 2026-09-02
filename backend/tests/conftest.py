"""测试公共夹具：临时数据库 + TestClient"""
import os
import tempfile

import pytest
from fastapi.testclient import TestClient

# 必须在导入 database / main 之前设置，确保测试使用独立的临时库
_TEST_DB = os.path.join(tempfile.gettempdir(), "word_riddle_test.db")
if os.path.exists(_TEST_DB):
    os.remove(_TEST_DB)
os.environ["DATABASE_PATH"] = _TEST_DB
os.environ["ADMIN_PASSWORD"] = "testpass"

from database import Base, engine, SessionLocal  # noqa: E402
from models import Riddle  # noqa: E402
import main  # noqa: E402


@pytest.fixture()
def client():
    """每个测试用全新的空表，不触发 lifespan 种子数据"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield TestClient(main.app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture()
def make_riddle(db):
    """返回一个快速构造字谜的函数"""
    def _build(**kw):
        defaults = dict(
            question="一口咬掉牛尾巴", answer="告", difficulty=1,
            grade=1, source="manual", status="active", quality="normal",
            likes=0, dislikes=0,
        )
        defaults.update(kw)
        r = Riddle(**defaults)
        db.add(r)
        db.commit()
        db.refresh(r)
        return r
    return _build
