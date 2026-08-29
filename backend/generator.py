import json
import random
import os
from openai import OpenAI
from dotenv import load_dotenv

from hanzi_chaizi import HanziChaizi

hc = HanziChaizi()

load_dotenv()

# 初始化 DeepSeek 客户端（兼容 OpenAI SDK）
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 加载年级字表
with open(os.path.join(BASE_DIR, "grade_chars.json"), "r", encoding="utf-8") as f:
    GRADE_CHARS = json.load(f)


# 只按年级随机选字，不筛选可拆性
def get_random_char(grade: int, publisher: str = None, term: int = None):
    """从指定年级和学期的字表中随机取一个汉字（不要求可拆分）"""
    # 如果未指定出版社，则合并所有出版社的字
    chars = []
    if publisher:
        grade_data = GRADE_CHARS.get(publisher, {})
        if isinstance(grade_data.get(str(grade)), dict):
            # chars = []
            if term:
                chars = grade_data.get(str(grade), {}).get(str(term), [])
            else:
                for term_chars in grade_data.get(str(grade), {}).values():
                    chars.extend(term_chars)
                chars = list(set(chars))
        # chars = GRADE_CHARS.get(publisher, {}).get(str(grade), [])
    else:
        # chars = []
        for pub_chars in GRADE_CHARS.values():
            grade_data = pub_chars.get(str(grade), {})
            if isinstance(grade_data, dict):
                if term:
                    chars.extend(grade_data.get(str(term), []))
                else:
                    for term_chars in grade_data.values():
                        chars.extend(term_chars)
            else:
                chars.extend(grade_data)
            # chars.extend(pub_chars.get(str(grade), []))
        chars = list(set(chars))
    if not chars:
        return None
    return random.choice(chars)


def generate_riddle_with_llm(grade: int, publisher: str = None, term: int = None):
    """调用 DeepSeek 生成谜面（拆字引导）"""
    char = get_random_char(grade, publisher, term)
    if not char:
        print(f"年级 {grade} {'第' + str(term) + '学期' if term else ''} 没有可用的字")
        return None

    # 获取部件的列表（hanzi_chaizi 返回可能多个拆分，取第一个）
    parts_list = hc.query(char)
    if parts_list:
        # 可拆分：使用原有的拆字引导 prompt
        parts = parts_list[0]  # 取第一个拆分方案
        parts_str = "、".join(parts)
        prompt = f"""你是一个为小学生设计字谜的游戏设计师。
    请根据下面提供的部件，创作一个有趣、简短的字谜。
    规则：
    - 谜底是汉字："{char}"
    - 这个字由这些部件组成：{parts_str}
    - 谜面要巧妙利用这些部件，但不能直接说出部件名称，要用比喻、故事、动作等表达
    - 适合{grade}年级{'上学期' if term == 1 else '下学期' if term == 2 else ''}小学生理解，不要太难
    - 只返回谜面本身，不要解释，不要谜底，不要标点之外的符号
    - 谜面长度控制在20字以内

    示例：
    字：明（部件：日、月）
    谜面：太阳落在月亮旁

    字：秋（部件：禾、火）
    谜面：左边绿，右边红，左右相遇起凉风

    现在请为字"{char}"生成谜面："""

    else:
        # 不可拆分：使用自由创作 prompt，让大模型自己想
        prompt = f"""你是一个为小学生设计字谜的游戏设计师。
    请为汉字"{char}"创作一个有趣、简短的字谜，适合{grade}年级{'上学期' if term == 1 else '下学期' if term == 2 else ''}小学生理解。
    规则：
    - 谜面要巧妙描述这个字的形状、结构或含义，但不能直接出现该字
    - 只返回谜面本身，不要解释，不要谜底，不要任何额外符号
    - 谜面长度控制在20字以内

    示例（字：心）：
    谜面：三个小点儿，藏在弯钩里

    示例（字：高）：
    谜面：一点一横长，口字在中央，下面开扇门，里面张张嘴

    现在请为字"{char}"生成谜面："""

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=80
        )
        riddle_question = response.choices[0].message.content.strip()
        # 清洗可能的引号
        riddle_question = riddle_question.strip('"''「」')
        return {
            "question": riddle_question,
            "answer": char,
            "difficulty": 1,
            "source": "ai",
            "grade": grade
        }
    except Exception as e:
        print(f"大模型生成失败: {e}")
        return None

