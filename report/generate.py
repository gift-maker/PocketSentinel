# 1. 导入库
import pymysql
from jinja2 import Template
from pathlib import Path

# 2. 连接数据库
import pymysql

conn = pymysql.connect(
    host='127.0.0.1',
    user='sentinel',
    password='Sentinel@2026',
    database='pocket_sentinel',
    charset='utf8mb4'
)
# 3. 查询分类汇总数据（饼图）
with conn.cursor() as cursor:
    cursor.execute("""SELECT c.main_cat, SUM(t.amount) AS total
    FROM fact_transactions t
    JOIN dim_categories c ON t.category_id = c.category_id
    WHERE t.direction = 1
    GROUP BY c.main_cat
    ORDER BY total DESC""")
    category_data = cursor.fetchall()
  
# 4. 查询每日支出数据（折线图）
    cursor.execute("""
        SELECT DATE(T.trade_time) AS trade_date, SUM(amount) AS total      
        FROM fact_transactions T
        WHERE direction = 1
        GROUP BY trade_date
        ORDER BY trade_date           
                   """)
    daily_data = cursor.fetchall()
# 5. 查询深夜消费数据（柱状图）
    cursor.execute("""
        SELECT HOUR(T.trade_time) AS trade_hour, SUM(amount) AS total
        FROM fact_transactions T
        WHERE direction = 1 AND (HOUR(T.trade_time) >= 22 OR HOUR(T.trade_time) < 4)
        GROUP BY trade_hour
        ORDER BY trade_hour


     """)
    night_data = cursor.fetchall()
    cursor.execute("""
    SELECT MIN(DATE(trade_time)), MAX(DATE(trade_time))
    FROM fact_transactions
    WHERE direction = 1
""")
    date_range = cursor.fetchone()
    start_date = str(date_range[0])
    end_date = str(date_range[1])
    cursor.execute("SELECT SUM(amount) FROM fact_transactions WHERE direction = 0")
    total_income = float(cursor.fetchone()[0] or 0)
    #收入分类查询
    cursor.execute("""
    SELECT  c.main_cat ,SUM(t.amount) AS total
    FROM fact_transactions t
    JOIN dim_categories c ON t.category_id = c.category_id
    WHERE t.direction = 0
    GROUP BY c.main_cat
    ORDER BY total DESC
                
    """) 
    income_data = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM fact_transactions WHERE direction = 1")
    total_expense = float(cursor.fetchone()[0] or 0)






# 6. 读取模板，渲染 HTML，写出文件
# 6. 渲染 HTML，写出文件
template_path = Path(__file__).parent / 'template.html'
template = Template(template_path.read_text(encoding='utf-8'))

html = template.render(
    category_labels=str([row[0] for row in category_data]),
    category_values=str([float(row[1]) for row in category_data]),
    daily_labels=str([str(row[0]) for row in daily_data]),
    daily_values=str([float(row[1]) for row in daily_data]),
    night_labels=str([str(row[0]) for row in night_data]),
    night_values=str([float(row[1]) for row in night_data]),
    start_date=start_date,
    end_date=end_date,
    income_labels=str([row[0] for row in income_data]),
    income_values=str([float(row[1]) for row in income_data]),
    total_income=total_income,
    total_expense=total_expense,
)

output_path = Path(__file__).parent / 'report.html'
output_path.write_text(html, encoding='utf-8')
print(f'报告已生成：{output_path}')   