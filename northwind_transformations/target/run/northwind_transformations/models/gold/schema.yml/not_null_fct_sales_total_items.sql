
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_items
from `northwind`.`fct_sales`
where total_items is null



  
  
    ) dbt_internal_test