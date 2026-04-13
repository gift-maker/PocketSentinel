USE pocket_sentinel;

INSERT INTO dim_categories (main_cat, sub_cat, is_essential) VALUES
('餐饮',   '综合',   1),
('交通',   '共享单车', 1),
('娱乐',   '游戏',   0),
('教育',   '校园消费', 1);
INSERT INTO dim_merchants (original_name, refined_name, category_id) VALUES
('武汉市洪山区鹏华综合商店', '珞珈山综合商店', 4),
('WD芒果电单车',           '芒果电单车',    2),
('湖北知音动漫有限公司',    '知音动漫',      3),
('武汉大学',               '武汉大学消费',  4);
INSERT INTO fact_transactions 
    (trade_time, trade_type, amount, direction, payment_method, status, trans_hash, peer_id, category_id, product_desc, raw_note)
VALUES
('2026-04-11 12:25:28', '商户消费', 10.00, 1, '零钱通', '支付成功', '42000030412026041113266250', 1, 4, '珞珈山综合商店消费', '/'),
('2026-04-11 12:17:49', '商户消费',  1.45, 1, '零钱通', '支付成功', '42000030952026041155844445', 2, 2, '芒果电单车-果币充值', '/'),
('2026-04-10 20:07:09', '商户消费',  1.45, 1, '零钱通', '支付成功', '42000030152026041071446003', 3, 3, '购买钱包', '/'),
('2026-04-10 17:24:04', '商户消费', 14.80, 1, '零钱通', '支付成功', '42000031072026041067663900', 4, 4, '武汉大学-消费', '/');
USE pocket_sentinel;

-- 先拿到刚插入的 category_id
UPDATE fact_transactions 
SET category_id = (SELECT category_id FROM dim_categories WHERE main_cat = '网购')
WHERE trans_id = 145;

UPDATE fact_transactions 
SET category_id = (SELECT category_id FROM dim_categories WHERE main_cat = '其他')
WHERE trans_id = 128;