
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_total_value
from `northwind`.`fct_sales`
where order_total_value is null



  
  
    ) dbt_internal_test