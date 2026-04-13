--按分类汇总本月支出，要求输出：一级分类、总金额、笔数。
USE pocket_sentinel;

UPDATE dim_merchants
SET category_id = 2
WHERE original_name = '湖北知音动漫有限公司';
UPDATE fact_transactions
SET category_id = 2
WHERE peer_id = 3;
SELECT   dim_categories.main_cat,SUM(fact_transactions.amount) AS total_amount,COUNT(*) AS transaction_count
FROM     fact_transactions
JOIN     dim_categories ON fact_transactions.category_id = dim_categories.category_id
WHERE    direction=1
GROUP BY   dim_categories.main_cat;
