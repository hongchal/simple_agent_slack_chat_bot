order_sql_query = '''
SELECT 
    o.id as order_id,   
    u.email as user_email,
    o.created_at as order_created_at,
    DATE_ADD(o.created_at, INTERVAL 9 HOUR) as korea_order_created_at,
    p.id as product_id,
    p.shipping_type as shipping_type,
    p.name as product_name,
    pv.price  / 1000 as price,
    i.item_cost,
    i.size,
    ofp.quantity as quantity,
    pv.price * ofp.quantity / 1000 as total_price,
    ic1.name as category_L1,
    ic2.name as category_L2
FROM orders o 
LEFT JOIN users as u on o.user_id = u.id
LEFT JOIN order_fulfillment_orders as ofo on o.id = ofo.order_id
LEFT JOIN order_fulfillment_products as ofp on ofo.id = ofp.order_fulfillment_id
LEFT JOIN picking_slips as ps on ofo.id = ps.order_fulfillment_order_id 
LEFT JOIN product_variants as pv on ofp.product_variant_id = pv.id
LEFT JOIN products as p on pv.product_id = p.id
LEFT JOIN internal_categories as ic1 on p.super_internal_category_id = ic1.id
LEFT JOIN internal_categories as ic2 on p.base_internal_category_id = ic2.id
LEFT JOIN product_variant_item_mapper as pvim on pv.id = pvim.variant_id 
LEFT JOIN (
    SELECT 
        id,
        IFNULL((unit_price / IF(unit_box_quantity=0, 1, unit_box_quantity)) * unit_bundle_quantity / 1000, 0) AS item_cost,
        size
    FROM items
) as i on pvim.item_id = i.id

'''