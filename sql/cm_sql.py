cm_sql_query = '''
SELECT 
    DATE(CONVERT_TZ(o.created_at, '+00:00', '+09:00')) AS order_date,
    ofo.order_id AS order_id,
    ofo.id AS order_fulfillment_order_id,
    ps.id AS picking_slip_id,
    o.shopify_order_name AS shopify_order,
    IF(o.user_id = 78223, "hp_othersite", ofo.sales_type) AS sales_type,
    (ofo.total - ofo.gift_card_total) * 0.975 / 1000 * 1250  - cogs_temp.total_cogs - shipping_fee_temp.shipping_fee_charged AS cm,
    ofo.total,
    ofo.gift_card_total,
    cogs_temp.total_cogs,
    shipping_fee_temp.shipping_fee_charged
FROM order_fulfillment_orders as ofo 
LEFT JOIN picking_slips as ps on ofo.id = ps.order_fulfillment_order_id 
LEFT JOIN order_fulfillments as off on ps.id = off.picking_slip_id
LEFT JOIN orders as o on ofo.order_id = o.id
LEFT JOIN order_discount_codes as odc on o.id = odc.order_id
LEFT JOIN (
    SELECT 
        ofp.order_fulfillment_id,
        SUM(psi.quantity * i.item_cost) as total_cogs
    FROM picking_slip_items as psi 
    LEFT JOIN order_fulfillment_products as ofp on psi.order_fulfillment_product_id = ofp.id 
    LEFT JOIN product_variants as pv on ofp.product_variant_id = pv.id 
    LEFT JOIN product_variant_item_mapper as pvim on pv.id = pvim.variant_id 
    LEFT JOIN (
        SELECT 
            id,
            IFNULL((unit_price / IF(unit_box_quantity=0, 1, unit_box_quantity)) * unit_bundle_quantity / 1000, 0) AS item_cost  
        FROM items
    ) as i on pvim.item_id = i.id 
    GROUP BY ofp.order_fulfillment_id
) as cogs_temp on cogs_temp.order_fulfillment_id = ofo.id 
LEFT JOIN (
    SELECT
        ps.id,
        IF(ofo.sales_type IN ("hp_dropship"), 0, COALESCE(fsc.total, dsc.total)) AS shipping_fee_charged
    FROM picking_slips as ps 
    LEFT JOIN daily_shipping_charges as dsc on ps.id = dsc.picking_slip_id 
    LEFT JOIN final_shipping_charges as fsc on ps.id = fsc.picking_slip_id 
    LEFT JOIN order_fulfillment_orders as ofo on ps.order_fulfillment_order_id = ofo.id 
) shipping_fee_temp on ps.id = shipping_fee_temp.id
'''