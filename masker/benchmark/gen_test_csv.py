# 这个脚本生成一个10万行的假账单 CSV，用来测试性能。自己写，思路：

# 前18行写说明文字（随便写）
# 后10万行每行9个字段，第9列（index 8）是随机的28位数字字符串
import csv
import random
import string

def random_order_id():
    return ''.join([str(random.randint(0, 9)) for _ in range(28)])

with open('/tmp/test_100k.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    
    # 前18行说明文字
    for i in range(18):
        writer.writerow([f'说明文字第{i+1}行'])
    
    # 10万行数据
    for _ in range(100000):
        writer.writerow([
            '2026-04-11 12:00:00',  # 交易时间
            '商户消费',              # 交易类型
            '测试商户',              # 交易对方
            '测试商品',              # 商品
            '支出',                  # 收/支
            str(random.randint(1, 500)),  # 金额
            '零钱通',               # 支付方式
            '支付成功',             # 状态
            random_order_id(),      # 交易单号（第9列）
            random_order_id(),      # 商户单号
            '/'                     # 备注
        ])

print('生成完成：/tmp/test_100k.csv')