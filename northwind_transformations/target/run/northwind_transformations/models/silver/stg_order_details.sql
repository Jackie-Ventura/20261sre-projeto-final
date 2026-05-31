
  
    
    
    
        
         


        
  

  insert into `northwind`.`stg_order_details__dbt_backup`
        ("order_id", "product_id", "unit_price", "quantity", "discount", "total_price")with raw_data as (
    select
        JSONExtractInt(data, 'order_id') as order_id,
        JSONExtractInt(data, 'product_id') as product_id,
        JSONExtractFloat(data, 'unit_price') as unit_price,
        JSONExtractInt(data, 'quantity') as quantity,
        JSONExtractFloat(data, 'discount') as discount
    from northwind.ingestion
    where tag = 'northwind_order_details.csv'
)

select
    order_id,
    product_id,
    unit_price,
    quantity,
    discount,
    (unit_price * quantity) * (1 - discount) as total_price
from raw_data
  