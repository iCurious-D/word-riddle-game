"""
汉字信息工具函数 - 本地计算部分

利用 pypinyin 和 hanzi_chaizi 库获取汉字的基础信息。
"""

from pypinyin import lazy_pinyin, Style
from hanzi_chaizi import HanziChaizi

# 初始化拆字库（全局实例，避免重复加载）
_chaizi = HanziChaizi()


def get_pinyin(char: str) -> str:
    """
    获取汉字的拼音（带声调）

    Args:
        char: 单个汉字

    Returns:
        拼音字符串，如 "míng"

    Examples:
        >>> get_pinyin("明")
        'míng'
    """
    result = lazy_pinyin(char, style=Style.TONE)
    return result[0] if result else ""


def get_pinyin_initial(char: str) -> str:
    """
    获取汉字的拼音首字母

    Args:
        char: 单个汉字

    Returns:
        首字母，如 "m"

    Examples:
        >>> get_pinyin_initial("明")
        'm'
    """
    result = lazy_pinyin(char, style=Style.FIRST_LETTER)
    return result[0] if result else ""


def get_strokes(char: str) -> int:
    """
    获取汉字的笔画数

    Args:
        char: 单个汉字

    Returns:
        笔画数，如 8

    Note:
        hanzi_chaizi 的返回格式：[结构, 部件1, 部件2, ...]
        笔画数需要其他方式获取，这里暂时返回 None
    """
    # hanzi_chaizi 不直接提供笔画数，需要从 API 获取
    # 这里返回 None，由爬虫补充
    return None


def get_structure(char: str) -> str:
    """
    获取汉字的结构类型

    Args:
        char: 单个汉字

    Returns:
        结构类型，如 "左右"、"上下"、"包围"、"独体"

    Examples:
        >>> get_structure("明")
        '左右'
        >>> get_structure("花")
        '上下'
    """
    result = _chaizi.query(char)
    if result and isinstance(result, list) and len(result) >= 1:
        structure = result[0]
        # 标准化结构类型
        structure_map = {
            "左右": "左右结构",
            "上下": "上下结构",
            "包围": "包围结构",
            "半包围": "半包围结构",
            "全包围": "全包围结构",
            "品字": "品字结构",
        }
        return structure_map.get(structure, f"{structure}结构")
    return "独体结构"


def get_decompose(char: str) -> str:
    """
    获取汉字的拆字部件

    Args:
        char: 单个汉字

    Returns:
        拆字描述，如 "日+月"

    Examples:
        >>> get_decompose("明")
        '日+月'
    """
    result = _chaizi.query(char)
    if result and isinstance(result, list) and len(result) >= 2:
        # result[0] 是结构，result[1:] 是部件
        parts = result[1:]
        return "+".join(parts)
    return ""


def get_all_local_info(char: str) -> dict:
    """
    一次性获取所有本地可计算的汉字信息

    Args:
        char: 单个汉字

    Returns:
        包含 pinyin, structure, decompose 的字典

    Examples:
        >>> get_all_local_info("明")
        {'pinyin': 'míng', 'structure': '左右结构', 'decompose': '日+月'}
    """
    return {
        "pinyin": get_pinyin(char),
        "structure": get_structure(char),
        "decompose": get_decompose(char),
    }


if __name__ == "__main__":
    # 测试
    test_chars = ["明", "林", "花", "人", "国"]
    for char in test_chars:
        info = get_all_local_info(char)
        print(f"{char}: {info}")
