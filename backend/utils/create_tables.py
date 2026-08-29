"""
建表脚本：创建 character_info 表

用法：
    cd backend
    python -m utils.create_tables
"""

from database import engine
from models import Base, CharacterInfo


def create_tables():
    """创建所有未存在的表"""
    print("开始创建数据表...")
    Base.metadata.create_all(bind=engine)
    print("[OK] character_info 表已创建")

    # 验证表是否存在
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if "character_info" in tables:
        columns = inspector.get_columns("character_info")
        print(f"\ncharacter_info 表结构：")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
    else:
        print("[FAIL] character_info 表创建失败")


if __name__ == "__main__":
    create_tables()
