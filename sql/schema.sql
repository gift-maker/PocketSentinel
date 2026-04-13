USE pocket_sentinel;
CREATE TABLE dim_categories(
category_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
main_cat VARCHAR(32) NOT NULL ,
sub_cat  VARCHAR(32) NOT NULL,
is_essential TINYINT(1) NOT NULL DEFAULT 0,
created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE dim_merchants(   

peer_id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
original_name VARCHAR(128) NOT NULL ,
refined_name VARCHAR(64),
category_id INT UNSIGNED,
FOREIGN KEY (category_id)REFERENCES dim_categories(category_id)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE fact_transactions(

trans_id    BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY ,
trade_time           DATETIME  NOT NULL,
trade_type           VARCHAR(32),
amount               DECIMAL(10,2) NOT NULL,
direction            TINYINT(1)  NOT NULL ,COMMENT  '1=支出 0=收入',
payment_method       VARCHAR(32),
status               VARCHAR(16),
trans_hash           CHAR(32)    NOT NULL UNIQUE,
peer_id              INT UNSIGNED,
category_id          INT UNSIGNED,
product_desc         VARCHAR(256),
raw_note             VARCHAR(256),
FOREIGN KEY (peer_id)      REFERENCES dim_merchants(peer_id),
FOREIGN KEY (category_id)  REFERENCES dim_categories(category_id),
INDEX idx_trade_time (trade_time),
INDEX idx_direction  (direction)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


