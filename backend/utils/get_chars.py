import re

raw_text = """
一 二 三 上 下
大 小 人 口 日
月 天 地
"""

# 用正则提取所有中文字符
chars = re.findall(r'[\u4e00-\u9fff]', raw_text)
# 去重并保持顺序
seen = set()
unique_chars = []
for c in chars:
    if c not in seen:
        seen.add(c)
        unique_chars.append(c)

print(unique_chars)
# 输出: ['一', '二', '三', '上', '下', '大', '小', '人', '口', '日', '月', '天', '地']


