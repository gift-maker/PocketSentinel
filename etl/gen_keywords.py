import pymysql
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv(Path(__file__).parent.parent / '.env')

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
8.像是上海设备租赁啥的是我洗衣服的，武汉大学的大多数都是我在学校吃饭。
9. 只输出 JSON，不要任何解释"""

response2 = client.chat.completions.create(
    model=os.getenv('LLM_MODEL'),
    messages=[{"role": "user", "content": review_prompt}]
)

result = response2.choices[0].message.content.strip()
if result.startswith('```'):
    result = result.split('\n', 1)[1]
    result = result.rsplit('```', 1)[0]

try:
    keywords = json.loads(result)
    output_path = Path(__file__).parent / 'rules' / 'keywords.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(keywords, f, ensure_ascii=False, indent=2)
    print(f"keywords.json 已更新，共 {len(keywords)} 个分类")
    print(json.dumps(keywords, ensure_ascii=False, indent=2))
except json.JSONDecodeError as e:
    print(f"LLM 返回的不是合法 JSON：{e}")
    print(result)