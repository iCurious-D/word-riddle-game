"""
汉字信息爬虫 - 在线 API 部分

调用 mxnzp.com 免费汉字 API 获取部首、释义、笔画数。
API 免费额度：1000 次/天
"""

import os
import time
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API 配置
MXNZP_API_URL = "https://www.mxnzp.com/api/convert/dictionary"
MXNZP_APP_ID = os.getenv("MXNZP_APP_ID", "")
MXNZP_APP_SECRET = os.getenv("MXNZP_APP_SECRET", "")


def fetch_char_api(char: str, timeout: int = 5, debug: bool = False) -> dict | None:
    """
    调用 mxnzp API 获取汉字信息

    Args:
        char: 单个汉字
        timeout: 请求超时时间（秒）

    Returns:
        包含 pinyin, radical, meaning, strokes 的字典，失败返回 None

    Examples:
        >>> result = fetch_char_api("明")
        >>> print(result)
        {'pinyin': 'míng', 'radical': '日', 'meaning': '亮，清楚...', 'strokes': 8}
    """
    if not MXNZP_APP_ID or not MXNZP_APP_SECRET:
        print("[ERROR] MXNZP_APP_ID 或 MXNZP_APP_SECRET 未配置")
        return None

    params = {
        "content": char,
        "app_id": MXNZP_APP_ID,
        "app_secret": MXNZP_APP_SECRET,
    }

    try:
        resp = requests.get(MXNZP_API_URL, params=params, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()

        if debug:
            print(f"[DEBUG] Response: {data}")

        if data.get("code") == 1 and data.get("data"):
            item = data["data"][0]
            # 释义可能很长且包含换行，提取有效内容
            raw = item.get("explanation", "")
            meaning = ""
            if raw:
                import re
                # 1. 去掉开头的 "字 \n\n " 格式
                text = re.sub(r'^.\s*\n+\s*', '', raw)
                # 2. 清理所有换行为空格
                text = text.replace('\n', ' ').strip()
                # 3. 优先提取现代释义（⒈⒉⒊ 格式）
                modern_match = re.search(r'[⒈⒉⒊\d][\s．.]*([\u4e00-\u9fa5，、；]+)', text)
                if modern_match:
                    # 提取从⒈开始到下一个⒉或句号的内容
                    start = text.find(modern_match.group(0))
                    segment = text[start:start + 50]
                    # 截断到第一个数字序号或句号
                    end_match = re.search(r'[⒉⒊⒋⒌⒍⒎⒏⒐]', segment[1:])
                    if end_match:
                        segment = segment[:end_match.start() + 1]
                    elif '。' in segment:
                        segment = segment[:segment.index('。') + 1]
                    meaning = segment.strip()
                else:
                    # 没有现代释义格式，取第一个逗号或句号前的内容
                    text = re.sub(r'^[\(\（].*?[\)\）]', '', text)  # 去掉开头的(会意...)等
                    for sep in ['。', '，', ',']:
                        if sep in text[:40]:
                            meaning = text[:text.index(sep) + 1]
                            break
                    if not meaning:
                        meaning = text[:30]
                # 4. 最终截断
                if len(meaning) > 40:
                    meaning = meaning[:40] + '...'

            return {
                "pinyin": item.get("pinyin", ""),
                "radical": item.get("radicals", ""),  # API 字段名是 radicals
                "meaning": meaning,
                "strokes": item.get("strokes"),
            }
        else:
            # 错误码 0 表示 app_id 或 app_secret 不合法
            if data.get("code") == 0:
                print("[ERROR] API 认证失败，请检查 app_id 和 app_secret")
            return None

    except requests.exceptions.Timeout:
        print(f"[TIMEOUT] 查询 '{char}' 超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] 查询 '{char}' 失败: {e}")
        return None


def batch_fetch_chars(chars: list, delay: float = 2.0, progress_callback=None) -> dict:
    """
    批量获取汉字信息

    Args:
        chars: 汉字列表
        delay: 每次请求间隔（秒），API 限流严格建议 2 秒以上
        progress_callback: 进度回调函数 callback(current, total)

    Returns:
        {char: info_dict} 的字典

    Note:
        API 免费额度 1000 次/天，请注意控制调用次数
    """
    results = {}
    failed = []
    total = len(chars)

    for i, char in enumerate(chars, 1):
        info = fetch_char_api(char)
        if info:
            results[char] = info
        else:
            failed.append(char)

        # 进度回调
        if progress_callback:
            progress_callback(i, total)

        # 延时
        if delay > 0 and i < total:
            time.sleep(delay)

    # 重试失败的（间隔更长）
    if failed:
        print(f"[RETRY] {len(failed)} 个字失败，5 秒后重试...")
        time.sleep(5)
        for char in failed:
            info = fetch_char_api(char)
            if info:
                results[char] = info
            time.sleep(3)  # 重试间隔更长

    return results


def check_api_quota() -> bool:
    """
    检查 API 是否可用（用一个常见字测试）

    Returns:
        True 表示可用，False 表示不可用
    """
    result = fetch_char_api("一")
    return result is not None


if __name__ == "__main__":
    # 测试
    print("测试 API 连接...")
    if check_api_quota():
        print("[OK] API 可用")

        test_chars = ["明", "林", "花"]
        print(f"\n测试查询: {test_chars}")

        for char in test_chars:
            info = fetch_char_api(char)
            print(f"{char}: {info}")
            time.sleep(0.5)
    else:
        print("[FAIL] API 不可用，请检查配置")
