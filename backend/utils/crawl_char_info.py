"""
批量爬取汉字信息并写入 CharacterInfo 表

读取 grade_chars.json 中的所有汉字，合并本地计算和 API 数据后入库。
支持断点续爬（自动跳过已有记录）。

用法：
    cd backend
    python -m utils.crawl_char_info

API 免费额度：1000 次/天，脚本会自动控制节奏。
"""

import json
import sys
import os

# 确保可以导入项目模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import CharacterInfo
from utils.char_utils import get_all_local_info
from utils.char_crawler import fetch_char_api
from utils.char_crawler import check_api_quota


def load_all_chars():
    """从 grade_chars.json 加载所有汉字并去重

    JSON 结构：{publisher: {grade: {term: [char, ...]}}}
    """
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "grade_chars.json"
    )
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_chars = set()
    for publisher, grades in data.items():
        for grade, terms in grades.items():
            for term, chars in terms.items():
                all_chars.update(chars)

    print(f"从 grade_chars.json 加载了 {len(all_chars)} 个不重复汉字")
    return sorted(all_chars)


def get_existing_chars(db):
    """获取数据库中已有的汉字集合"""
    existing = db.query(CharacterInfo.char).all()
    return set(row[0] for row in existing)


def crawl_and_save(max_chars: int = None):
    """
    批量爬取并入库

    Args:
        max_chars: 最多处理多少个（None 表示全部）
    """
    db = SessionLocal()

    try:
        # 1. 加载字表
        all_chars = load_all_chars()

        # 2. 跳过已有记录
        existing = get_existing_chars(db)
        remaining = [c for c in all_chars if c not in existing]
        print(f"数据库已有 {len(existing)} 个字，剩余 {len(remaining)} 个待处理")

        if max_chars and max_chars < len(remaining):
            remaining = remaining[:max_chars]
            print(f"本次限制处理 {max_chars} 个")

        if not remaining:
            print("[DONE] 没有需要处理的汉字")
            return

        # 3. 测试 API
        print("\n测试 API 连接...")
        if not check_api_quota():
            print("[ERROR] API 不可用，请检查配置或稍后再试")
            return

        # 4. 开始处理
        import time
        success = 0
        api_fail = 0
        total = len(remaining)
        delay = 2.0  # 请求间隔（秒）

        print(f"\n开始处理 {total} 个汉字...\n")

        for i, char in enumerate(remaining, 1):
            # 本地计算
            local = get_all_local_info(char)

            # API 获取
            api_data = fetch_char_api(char)

            try:
                if api_data:
                    info = CharacterInfo(
                        char=char,
                        pinyin=api_data.get("pinyin") or local.get("pinyin"),
                        radical=api_data.get("radical"),
                        strokes=api_data.get("strokes"),
                        structure=local.get("structure"),
                        meaning=api_data.get("meaning"),
                        decompose=local.get("decompose"),
                    )
                    db.add(info)
                    db.commit()
                    success += 1
                else:
                    # API 失败，只存本地数据
                    info = CharacterInfo(
                        char=char,
                        pinyin=local.get("pinyin"),
                        radical=None,
                        strokes=None,
                        structure=local.get("structure"),
                        meaning=None,
                        decompose=local.get("decompose"),
                    )
                    db.add(info)
                    db.commit()
                    api_fail += 1
            except Exception:
                # 重复插入或其他错误，跳过
                db.rollback()
                api_fail += 1

            # 进度显示（每 10 个打印一次）
            if i % 10 == 0 or i == total:
                print(f"  进度: {i}/{total} | 成功: {success} | API失败: {api_fail}")

            # 延时
            if i < total:
                time.sleep(delay)

        print(f"\n[DONE] 处理完成: 成功 {success}, API失败(仅本地) {api_fail}")
        print(f"数据库现有 {len(get_existing_chars(db))} 条汉字信息")

    except KeyboardInterrupt:
        print("\n[STOP] 用户中断，已保存当前进度")
    except Exception as e:
        print(f"[ERROR] {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="批量爬取汉字信息入库")
    parser.add_argument("--max", type=int, default=None, help="最多处理多少个汉字")
    args = parser.parse_args()

    crawl_and_save(max_chars=args.max)
