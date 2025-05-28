pre_shipped_sql_query = '''
select 
    ofo.sales_type                                                as sales_type,
    convert_tz(psi.pre_order_shipping_at, '+00:00', 'Asia/Seoul') as kr_pre_order_shipping_at,
    c.name                                                        as company_name,
    psi.item_id                                                   as item_id,
    i.name                                                        as item_name,
    SUM(psi.quantity - psi.refunded_quantity)                     as quantity,
from picking_slip_items psi
left join order_fulfillments odf on odf.picking_slip_id = psi.picking_slip_id
join order_fulfillment_orders ofo on odf.order_fulfillment_order_id = ofo.id
left join items i on psi.item_id = i.id
left join picking_slip_dates psd on psd.picking_slip_id = psi.picking_slip_id
left join companies c on i.company_id = c.id
where 1=1
  and psi.quantity - psi.refunded_quantity > 0
GROUP BY ofo.sales_type,
         convert_tz(psi.pre_order_shipping_at, '+00:00', 'Asia/Seoul'),
         c.name,
         psi.item_id,
         i.id,
         i.name;
'''