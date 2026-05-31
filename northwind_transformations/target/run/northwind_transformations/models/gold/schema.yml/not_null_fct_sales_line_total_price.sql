
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select line_total_price
from `northwind`.`fct_sales`
where line_total_price is null



  
  
    ) dbt_internal_test