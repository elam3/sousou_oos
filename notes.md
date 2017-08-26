Sat Aug 26 15:48:29 PDT 2017
mysql> select distinct post_status from wp_posts;
+---------------+
| post_status   |
+---------------+
| inherit       |
| draft         |
| private       |
| publish       |
| auto-draft    |
| trash         |
| pending       |
| wc-cancelled  |
| wc-completed  |
| wc-failed     |
| wc-on-hold    |
| wc-pending    |
| wc-processing |
| wc-refunded   |
+---------------+
14 rows in set (0.20 sec)

mysql> describe wp_posts;
+-----------------------+---------------------+------+-----+---------------------+----------------+
| Field                 | Type                | Null | Key | Default             | Extra          |
+-----------------------+---------------------+------+-----+---------------------+----------------+
| ID                    | bigint(20) unsigned | NO   | PRI | NULL                | auto_increment |
| post_author           | bigint(20) unsigned | NO   | MUL | 0                   |                |
| post_date             | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_date_gmt         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_content          | longtext            | NO   |     | NULL                |                |
| post_title            | text                | NO   |     | NULL                |                |
| post_excerpt          | text                | NO   |     | NULL                |                |
| post_status           | varchar(20)         | NO   |     | publish             |                |
| comment_status        | varchar(20)         | NO   |     | open                |                |
| ping_status           | varchar(20)         | NO   |     | open                |                |
| post_password         | varchar(20)         | NO   |     |                     |                |
| post_name             | varchar(200)        | NO   | MUL |                     |                |
| to_ping               | text                | NO   |     | NULL                |                |
| pinged                | text                | NO   |     | NULL                |                |
| post_modified         | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_modified_gmt     | datetime            | NO   |     | 0000-00-00 00:00:00 |                |
| post_content_filtered | longtext            | NO   |     | NULL                |                |
| post_parent           | bigint(20) unsigned | NO   | MUL | 0                   |                |
| guid                  | varchar(255)        | NO   |     |                     |                |
| menu_order            | int(11)             | NO   |     | 0                   |                |
| post_type             | varchar(20)         | NO   | MUL | post                |                |
| post_mime_type        | varchar(100)        | NO   |     |                     |                |
| comment_count         | bigint(20)          | NO   |     | 0                   |                |
+-----------------------+---------------------+------+-----+---------------------+----------------+
23 rows in set (0.00 sec)



mysql> select distinct post_type from wp_posts;
+-------------------+
| post_type         |
+-------------------+
| attachment        |
| ign_voucher       |
| nav_menu_item     |
| optionsframework  |
| page              |
| post              |
| product           |
| product_variation |
| revision          |
| shop_coupon       |
| shop_order        |
| shop_order_refund |
| shop_rewards      |
| sidebars          |
| wpsc-product-file |
+-------------------+
15 rows in set (0.00 sec)


distinct meta_key from wp_postmeta
| Yen Price                                     |
| yen                                           |
| _stock                                        |
| _stock_status                                 |
| _manage_stock                                 |

| cotton scarf nandin                           |
| noren                                         |
| noren curtain                                 |
| kimonodress                                   |
| wallet, gamaguchi, sousou, kyoto, japan       |
| tenugui,                                      |
| product_categories                            |
| sousounetshopURL                              |
| test                                          |



mysql> select distinct meta_value from wp_postmeta where meta_key = '_stock_status';
+------------+
| meta_value |
+------------+
| outofstock |
| instock    |
+------------+
2 rows in set (0.12 sec)

mysql> select distinct meta_value from wp_postmeta where meta_key = '_manage_stock';
+------------+
| meta_value |
+------------+
| no         |
| yes        |
+------------+
2 rows in set (0.11 sec)

---- ---- ---- ---- ----
    Query Drafts
---- ---- ---- ---- ----
select post_id, meta_key, meta_value from wp_postmeta where meta_key = '_stock'

