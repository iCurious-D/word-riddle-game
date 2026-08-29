"""
迁移脚本：给 riddles 表新增评价系统字段

用法：
    cd backend
    python -m utils.migrate_riddles
"""

import sqlite3
import os


def migrate():
    db_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "riddles.db"
    )
    if not os.path.exists(db_path):
        print(f"[ERROR] riddles.db not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取现有列
    cursor.execute("PRAGMA table_info(riddles)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    print(f"Existing columns: {sorted(existing_columns)}")

    # 需要新增的列 (列名, 类型, 默认值)
    new_columns = [
        ("likes", "INTEGER", "0"),
        ("dislikes", "INTEGER", "0"),
        ("quality", "VARCHAR(10)", "'normal'"),
        ("status", "VARCHAR(10)", "'active'"),
        ("submitter", "VARCHAR(50)", "NULL"),
    ]

    added = 0
    for col_name, col_type, default in new_columns:
        if col_name in existing_columns:
            print(f"  [SKIP] {col_name} already exists")
        else:
            sql = f"ALTER TABLE riddles ADD COLUMN {col_name} {col_type} DEFAULT {default}"
            cursor.execute(sql)
            print(f"  [ADD] {col_name} ({col_type}, default={default})")
            added += 1

    if added > 0:
        conn.commit()
        print(f"\n[OK] Added {added} column(s) to riddles table")
    else:
        print("\n[OK] No migration needed, all columns exist")

    # 验证
    cursor.execute("PRAGMA table_info(riddles)")
    columns = cursor.fetchall()
    print(f"\nRiddles table now has {len(columns)} columns:")
    for col in columns:
        print(f"  - {col[1]}: {col[2]}")

    conn.close()


if __name__ == "__main__":
    migrate()
