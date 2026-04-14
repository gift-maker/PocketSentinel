#!/usr/bin/env bash
set -euo pipefail   # 任意步骤失败即退出

# 接收参数：输入文件路径
CSV_FILE=$1
MASKED_FILE=~/pocketsentinel/data/masked/$(basename $CSV_FILE)
# Step 1: C++ 脱敏
echo "Step 1: 脱敏处理..."
~/pocketsentinel/masker/build/masker $CSV_FILE $MASKED_FILE
# Step 2: Python ETL
echo "Step 2: 入库处理..."
cd ~/pocketsentinel/etl && python3 ingest.py $MASKED_FILE
# Step 3: 打印完成
echo " 完成 "
