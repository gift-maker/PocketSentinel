import json
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

RULES_PATH = Path(__file__).parent / 'rules' / 'keywords.json'
ALLOWED_CATEGORIES = {
    '餐饮', '交通', '购物', '娱乐', '教育', '转账', '住宿', '理财', '还款', '其他'
}

def classify_by_rules(merchant_name: str):
    # 1. 读取 keywords.json
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        rules = json.load(f)
    # 2. 遍历每个分类
    for cat_name,cat_info in rules.items():
        for keywords in cat_info['keywords']:
    # 3. 检查 merchant_name 里有没有包含该分类的任意一个 keyword
            if keywords in merchant_name:
    # 4. 有就返回这个分类的信息，没有返回 None
               return cat_info
  
    return None
# 读取 .env 里的 key 和 base_url
# 构造一个 prompt，告诉 LLM 商户名，让它返回分类
# 返回分类名字符串，比如「餐饮」「交通」
def classify_by_llm(merchant_name: str) -> str | None:
    # 1. 加载 .env
    load_dotenv()
    # 2. 初始化 OpenAI 客户端，传入 api_key 和 base_url
    try:
        client = OpenAI(
            api_key=os.getenv('LLM_API_KEY'),
            base_url=os.getenv('LLM_BASE_URL')
        )
        # 3. 构造 prompt，告诉 LLM 商户名，让它返回分类
        prompt = (
            "你是账单分类器。"
            f"商户名: {merchant_name}\n"
            "可选分类仅限：餐饮、交通、购物、娱乐、教育、转账、住宿、理财、还款、其他。\n"
            "只返回一个分类名称，不要解释，不要新增分类。"
        )
        # 4. 调用 client.chat.completions.create()
        response = client.chat.completions.create(
            model=os.getenv('LLM_MODEL'),
            temperature=0,
            max_tokens=16,
            messages=[
                {"role": "system", "content": "你只能返回给定集合中的一个分类名称。"},
                {"role": "user", "content": prompt}
            ]
        )
        # 5. 取出返回的分类名，strip() 去掉空格
        category = response.choices[0].message.content.strip().replace('"', '')
        # 防止模型返回句子/解释，先按常见分隔符截断
        for sep in ['\n', '，', ',', '。', ':', '：']:
            if sep in category:
                category = category.split(sep, 1)[0].strip()
        # 6. 返回分类名字符串，出错返回 None
        if category in ALLOWED_CATEGORIES:
            return category
        # 出现幻觉时兜底到“其他”，避免污染 dim_categories
        return '其他'
    except Exception as e:
        print(f"LLM 调用失败: {e}")
        return None

if __name__ == '__main__':
    print(classify_by_rules('武汉大学'))
    print(classify_by_rules('WD芒果电单车'))
    print(classify_by_llm('Enen'))