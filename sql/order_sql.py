order_sql_query = '''
 SELECT 
    o.id as order_id,   
    u.email as user_email,
    o.created_at as order_created_at,
    p.id as product_id,
    p.name as product_name,
    pv.price as price
FROM orders o 
LEFT JOIN users as u on o.user_id = u.id
LEFT JOIN order_fulfillment_orders as ofo on o.id = ofo.order_id
LEFT JOIN order_fulfillment_products as ofp on ofo.id = ofp.order_fulfillment_id
LEFT JOIN product_variants as pv on ofp.product_variant_id = pv.id
LEFT JOIN products as p on pv.product_id = p.id
'''