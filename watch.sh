#!/usr/bin/env bash

RAW_DIR=~/pocketsentinel/data/raw

echo "开始监听目录: $RAW_DIR"

inotifywait -m "$RAW_DIR" -e close_write --format '%w%f' |
while read NEWFILE; do
    if [[ "$NEWFILE" == *.csv ]]; then
        echo "检测到新文件: $NEWFILE"
        bash ~/pocketsentinel/pipeline.sh "$NEWFILE"
    fi
done