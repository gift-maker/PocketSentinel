#!/usr/bin/env bash

# 找到桌面上最新的微信账单 xlsx
XLSX=$(ls /mnt/c/Users/cuixi/Desktop/微信支付账单*.xlsx 2>/dev/null | sort | tail -1)

if [ -z "$XLSX" ]; then
    echo "桌面上没有找到微信账单文件"
    read -p "按回车退出..."
    exit 1
fi

echo "找到账单：$XLSX"

# 转成 CSV
python3 -c "
import openpyxl, csv
from pathlib import Path

wb = openpyxl.load_workbook('$XLSX')
ws = wb.active
with open('/home/cuixi/pocketsentinel/data/raw/latest_bill.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for row in ws.iter_rows(values_only=True):
        writer.writerow(['' if v is None else str(v) for v in row])
print('转换完成')
"

# 触发流水线
bash ~/pocketsentinel/pipeline.sh ~/pocketsentinel/data/raw/latest_bill.csv

# 生成月报
cd ~/pocketsentinel/report && python3 generate.py

# 打开浏览器
explorer.exe $(wslpath -w ~/pocketsentinel/report/report.html)