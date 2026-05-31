
  
    
    
    
        
         


        
  

  insert into `northwind`.`stg_orders__dbt_backup`
        ("order_id", "customer_id", "employee_id", "order_date", "freight", "ship_country")with raw_data as (
    select
        JSONExtractString(data, 'order_id') as order_id,
        JSONExtractString(data, 'customer_id') as customer_id,
        JSONExtractInt(data, 'employee_id') as employee_id,
        JSONExtractString(data, 'order_date') as order_date,
        JSONExtractFloat(data, 'freight') as freight,
        JSONExtractString(data, 'ship_country') as ship_country
    from northwind.ingestion
    where tag = 'northwind_orders.csv'
)

select
    toInt64(order_id) as order_id,
    customer_id,
    employee_id,
    toDate(order_date) as order_date,
    freight,
    ship_country
from raw_data
  