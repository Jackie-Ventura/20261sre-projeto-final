with orders as (
    select * from `northwind`.`stg_orders`
),
details as (
    select 
        order_id,
        product_id,
        total_price as line_total_price,
        quantity
    from `northwind`.`stg_order_details`
)

select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.ship_country,
    d.product_id,
    d.line_total_price,
    d.quantity
from orders o
inner join details d on o.order_id = d.order_id