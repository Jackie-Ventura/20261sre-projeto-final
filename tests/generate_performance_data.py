import csv
import os
import random
from datetime import datetime, timedelta

def generate_orders(num_rows, output_path):
    headers = [
        "order_id", "customer_id", "employee_id", "order_date", "required_date", 
        "shipped_date", "ship_via", "freight", "ship_name", "ship_address", 
        "ship_city", "ship_region", "ship_postal_code", "ship_country"
    ]
    
    customers = ["VINET", "TOMSP", "HANAR", "VICTE", "SUPRD", "CHOPS", "RICAR", "WELLI"]
    countries = ["France", "Germany", "Brazil", "Belgium", "Switzerland", "Venezuela", "Austria"]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        
        start_date = datetime(1996, 1, 1)
        
        for i in range(num_rows):
            order_id = 10000 + i
            customer = random.choice(customers)
            employee = random.randint(1, 10)
            order_date = start_date + timedelta(days=random.randint(0, 1000))
            req_date = order_date + timedelta(days=30)
            ship_date = order_date + timedelta(days=random.randint(1, 10))
            ship_via = random.randint(1, 3)
            freight = round(random.uniform(10.0, 100.0), 2)
            
            writer.writerow([
                order_id, customer, employee, 
                order_date.strftime('%Y-%m-%d'), 
                req_date.strftime('%Y-%m-%d'), 
                ship_date.strftime('%Y-%m-%d'),
                ship_via, freight, f"Ship {i}", f"Address {i}", "City", "Region", "12345", random.choice(countries)
            ])

if __name__ == "__main__":
    import sys
    rows = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    path = sys.argv[2] if len(sys.argv) > 2 else "dados_performance/perf_orders.csv"
    print(f"Gerando {rows} linhas em {path}...")
    generate_orders(rows, path)
    print("Concluído.")
