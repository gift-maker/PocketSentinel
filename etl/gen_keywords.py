import pymysql
import json
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / '.env')

ALLOWED_CATEGORIES = [
    '餐饮', '交通', '购物', '娱乐', '教育', '转账', '住宿', '理财', '还款', '其他'
]


def _is_valid_keyword(keyword: str, merchants: list[str]) -> bool:
    kw = keyword.strip()
    if not kw:
        return False
    # 过滤明显无意义占位符
    if kw in {'/', '-', '_', '.', '...'}:
        return False
    # 过滤过短噪声关键词（尤其是单字符）
    if len(kw) <= 1:
        return False
    # 过滤纯英文/数字且过短的噪声片段
    if re.fullmatch(r'[A-Za-z0-9_\-*]+', kw) and len(kw) < 3:
        return False
    # 关键词必须是商户列表中的完整商户名，彻底抑制模型编造“片段词”
    return kw in set(merchants)


def _collect_all_keywords(rules: dict) -> list[str]:
    return [kw for cat in ALLOWED_CATEGORIES for kw in rules[cat]['keywords']]


def _move_keyword(rules: dict, keyword: str, target_cat: str):
    if target_cat not in rules:
        return
    for cat in ALLOWED_CATEGORIES:
        if keyword in rules[cat]['keywords']:
            rules[cat]['keywords'].remove(keyword)
    if keyword not in rules[target_cat]['keywords']:
        rules[target_cat]['keywords'].append(keyword)


def enforce_business_rules(rules: dict) -> dict:
    # 你的明确偏好：武汉大学归餐饮
    force_to_food = {
        '武汉大学'
    }
    for kw in force_to_food:
        _move_keyword(rules, kw, '餐饮')

    # 你的明确偏好：上海众家联设备租赁有限公司归其他（洗衣相关）
    _move_keyword(rules, '上海众家联设备租赁有限公司', '其他')

    # 理发相关：明确不是娱乐，统一归到其他
    hair_patterns = ['造型', '发艺', '理发', '美发', '美发店']

    # 规则关键词映射（命中后强制移动）
    keyword_rules = [
        ('转账', ['发给', '红包', '转账', '妈妈', '爸爸', '家人', '朋友', '同学']),
        ('还款', ['银行', '信用卡', '还款']),
        ('理财', ['理财', '基金', '零钱通', '理财通']),
        ('购物', ['超市', '便利店', '生鲜']),
        ('住宿', ['宾馆', '酒店', '民宿', '旅馆']),
        ('娱乐', ['游戏', '软件', '订阅', '会员'])
    ]

    all_kw = _collect_all_keywords(rules)
    for kw in all_kw:
        if any(p in kw for p in hair_patterns):
            _move_keyword(rules, kw, '其他')
            continue

        for target_cat, patterns in keyword_rules:
            if any(p in kw for p in patterns):
                _move_keyword(rules, kw, target_cat)
                break

    return rules


def enforce_unique_assignment(rules: dict) -> dict:
    # 每个商户关键词只保留在一个分类中，按优先级决策归属。
    priority = ['转账', '还款', '理财', '住宿', '购物', '交通', '餐饮', '娱乐', '教育', '其他']
    owner: dict[str, str] = {}

    for cat in priority:
        unique_keywords = []
        seen_in_cat = set()
        for kw in rules[cat]['keywords']:
            if kw in seen_in_cat:
                continue
            seen_in_cat.add(kw)
            if kw in owner:
                continue
            owner[kw] = cat
            unique_keywords.append(kw)
        rules[cat]['keywords'] = unique_keywords

    return rules


def normalize_rules(raw_rules: dict, merchants: list[str]) -> dict:
    merchant_set = set(merchants)
    dropped_keywords: list[tuple[str, str]] = []

    normalized = {
        cat: {
            'main_cat': cat,
            'sub_cat': '综合',
            'is_essential': 1,
            'keywords': []
        }
        for cat in ALLOWED_CATEGORIES
    }

    for cat, cat_info in raw_rules.items():
        if cat not in normalized or not isinstance(cat_info, dict):
            continue

        seen = set(normalized[cat]['keywords'])
        for kw in cat_info.get('keywords', []):
            if not isinstance(kw, str):
                continue
            kw = kw.strip()
            if kw in seen:
                continue
            if kw in merchant_set and _is_valid_keyword(kw, merchants):
                normalized[cat]['keywords'].append(kw)
                seen.add(kw)
            else:
                dropped_keywords.append((cat, kw))

    # 执行硬性业务规则纠偏（即使 LLM 不听话也会被修正）
    normalized = enforce_business_rules(normalized)
    # 一个商户只允许落在一个分类，防止跨类重复
    normalized = enforce_unique_assignment(normalized)

    # 把未被任何关键词覆盖的商户，兜底放入“其他”
    all_keywords = [kw for cat in ALLOWED_CATEGORIES for kw in normalized[cat]['keywords']]
    uncategorized = [m for m in merchants if not any(kw in m for kw in all_keywords)]
    for m in uncategorized:
        if _is_valid_keyword(m, merchants) and m not in normalized['其他']['keywords']:
            normalized['其他']['keywords'].append(m)

    if dropped_keywords:
        print(f"过滤掉 {len(dropped_keywords)} 个可疑关键词（非完整商户名或噪声）")
        for cat, kw in dropped_keywords[:20]:
            print(f"  - [{cat}] {kw}")
        if len(dropped_keywords) > 20:
            print(f"  ... 其余 {len(dropped_keywords) - 20} 个已省略")

    return normalized

conn = pymysql.connect(
    host='127.0.0.1',
    user='sentinel',
    password='Sentinel@2026',
    database='pocket_sentinel',
    charset='utf8mb4'
)

with conn.cursor() as cursor:
    cursor.execute("SELECT DISTINCT original_name FROM dim_merchants")
    merchants = [row[0] for row in cursor.fetchall()]

print(f"共 {len(merchants)} 个商户，正在让 LLM 分类...")

client = OpenAI(
    api_key=os.getenv('LLM_API_KEY'),
    base_url=os.getenv('LLM_BASE_URL')
)

prompt = f"""以下是微信账单中出现的所有商户名，请帮我生成分类规则字典。

商户列表：
{chr(10).join(merchants)}

严格要求：
1. 分类只能是以下10个之一：餐饮、交通、购物、娱乐、教育、转账、住宿、理财、还款、其他
2. 把所有商户归入这10个分类，不要创建新分类
3. keywords 只能是商户列表中实际出现的词或片段，不能添加列表之外的词
4. 同类商户的关键词合并到同一个分类下
5. 只输出 JSON，不要任何解释，格式：
{{
  "餐饮": {{
    "main_cat": "餐饮",
    "sub_cat": "综合",
    "is_essential": 1,
    "keywords": ["关键词1", "关键词2"]
  }}
}}"""

response = client.chat.completions.create(
    model=os.getenv('LLM_MODEL'),
    temperature=0,
    messages=[{"role": "user", "content": prompt}]
)

result = response.choices[0].message.content.strip()
if result.startswith('```'):
    result = result.split('\n', 1)[1]
    result = result.rsplit('```', 1)[0]

review_prompt = f"""请检查并修正以下微信账单商户分类规则字典：

{result}

修正原则：
1. 人名、朋友、家人相关的商户归入「转账」
2. 银行相关归入「还款」
3. 理财相关归入「理财」
4. 超市、便利店、生鲜归入「购物」
5. 旅行、宾馆、酒店归入「住宿」
6. 游戏、软件、订阅服务归入「娱乐」
7. 分类只能是：餐饮、交通、购物、娱乐、教育、转账、住宿、理财、还款、其他，不要创建新分类
8.像是上海设备租赁啥的是我洗衣服的，武汉大学的大多数都是我在学校吃饭。归入餐饮
9.再就是有一些什么造型，发艺的是我在理发的花费不是娱乐
10.不要加其他的词不要出现幻觉，keywords 只能是商户列表中实际出现的词或片段，不能添加列表之外的词
11. 只输出 JSON，不要任何解释"""

response2 = client.chat.completions.create(
    model=os.getenv('LLM_MODEL'),
    temperature=0,
    messages=[{"role": "user", "content": review_prompt}]
)

result = response2.choices[0].message.content.strip()
if result.startswith('```'):
    result = result.split('\n', 1)[1]
    result = result.rsplit('```', 1)[0]

try:
    keywords = json.loads(result)
    keywords = normalize_rules(keywords, merchants)
    output_path = Path(__file__).parent / 'rules' / 'keywords.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)
    print(f"keywords.json 已更新，共 {len(keywords)} 个分类")
    print(json.dumps(keywords, ensure_ascii=False, indent=2))
except json.JSONDecodeError as e:
    print(f"LLM 返回的不是合法 JSON：{e}")
    print(result)