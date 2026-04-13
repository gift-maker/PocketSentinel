# PocketSentinel 口袋哨兵

> 微信账单智能审计系统 —— 基于 C++ / Python / MySQL / Linux 的本地化 ETL 流水线

## 项目简介

自动处理微信导出的账单文件，实现从原始 xlsx 到结构化数据库的全程自动化，
并生成可视化消费月报。所有数据本地处理，隐私不上云。

## 技术栈

| 模块 | 技术 |
|---|---|
| 脱敏层 | C++ 17 / OpenSSL SHA-256 |
| 数据处理 | Python / openpyxl / pymysql |
| 分类引擎 | 规则字典 + 千问 LLM API |
| 数据库 | MySQL 8.0 / 星型模型 |
| 自动化 | Linux Shell / inotifywait |
| 可视化 | Jinja2 / Chart.js |

## 系统架构
微信账单 xlsx
↓ Python 转 CSV
C++ Masker（SHA-256 脱敏）
↓
Python ETL（清洗 + 分类 + 入库）
↓
MySQL（星型模型：fact_transactions + dim_categories + dim_merchants）
↓
HTML 月报（饼图 + 折线图 + 柱状图）
## Performance Benchmark

测试数据：100 万行 CSV

| 实现 | 耗时 |
|---|---|
| C++ Masker | 3.199s |
| Python hashlib | 0.111s |

**结论**：Python csv 模块底层为 C 实现，在批量 CSV 处理上更快。
选择 C++ 的原因是架构隔离而非性能——脱敏在数据进入 Python 层之前完成。
## 快速开始

1. 把微信账单 xlsx 放到 Windows 桌面
2. 双击桌面快捷方式（或运行 `bash run.sh`）
3. 浏览器自动打开消费月报

## Performance Benchmark

测试数据：100 万行 CSV

| 实现 | 耗时 |
|---|---|
| C++ Masker | 3.199s |
| Python hashlib | 0.111s |

结论：Python csv 模块底层为 C 实现，批量处理更快。
选择 C++ 的原因是架构隔离——脱敏在数据进入 Python 层之前完成。

## 目录结构
pocketsentinel/
├── masker/          # C++ 脱敏工具
├── etl/             # Python ETL 引擎
├── sql/             # 建表脚本 + 聚合查询
├── report/          # HTML 月报生成器
├── data/            # 数据目录
│   ├── raw/         # 原始 CSV
│   └── masked/      # 脱敏后 CSV
└── run.sh           # 一键运行脚本