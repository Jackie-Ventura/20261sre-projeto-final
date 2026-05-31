import os
import csv
import clickhouse_connect
import pandas as pd
from dotenv import load_dotenv
import subprocess
import json

load_dotenv()

def get_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "northwind"),
        database=os.getenv("CLICKHOUSE_DB", "northwind")
    )

def test_data_integrity():
    print("--- Iniciando Teste de Adequação Funcional (Integridade) ---")
    
    # 1. Preparar dados de teste
    test_dir = "dados_teste_integridade"
    os.makedirs(test_dir, exist_ok=True)
    csv_path = os.path.join(test_dir, "integrity_orders.csv")
    
    num_rows = 1000
    expected_freight_sum = 0
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["order_id", "freight", "customer_id"])
        for i in range(num_rows):
            freight = round(10.5 * (i + 1), 2)
            expected_freight_sum += freight
            writer.writerow([i + 10000, freight, f"CUST_{i}"])
    
    print(f"Gerado CSV com {num_rows} linhas. Soma esperada do Freight: {expected_freight_sum:.2f}")

    # 2. Limpar tabela de ingestão
    client = get_client()
    client.command("TRUNCATE TABLE ingestion")
    print("Tabela 'ingestion' limpa.")

    # 3. Executar ingestão
    env = os.environ.copy()
    env["CSV_DATA_DIR"] = test_dir
    env["CLICKHOUSE_PASSWORD"] = "northwind" # Garantindo que a senha correta seja usada
    
    print("Executando script de ingestão...")
    result = subprocess.run(["python3", "scripts/ingestion.py"], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Erro na ingestão:")
        print(result.stderr)
        return False

    # 4. Validar resultados no ClickHouse
    print("Validando dados no ClickHouse...")
    
    # Contagem de linhas
    actual_rows = client.command("SELECT count() FROM ingestion WHERE tag = 'integrity_orders.csv'")
    
    # Soma do Freight (extraindo do JSON)
    # No ClickHouse: JSONExtractFloat(data, 'freight')
    actual_freight_sum = client.command("""
        SELECT sum(JSONExtractFloat(data, 'freight')) 
        FROM ingestion 
        WHERE tag = 'integrity_orders.csv'
    """)
    
    # Verificação de IDs (Min/Max)
    min_id = client.command("SELECT min(JSONExtractInt(data, 'order_id')) FROM ingestion WHERE tag = 'integrity_orders.csv'")
    max_id = client.command("SELECT max(JSONExtractInt(data, 'order_id')) FROM ingestion WHERE tag = 'integrity_orders.csv'")

    print(f"\nResultados:")
    print(f"- Linhas: Esperado {num_rows}, Obtido {actual_rows}")
    print(f"- Soma Freight: Esperado {expected_freight_sum:.2f}, Obtido {actual_freight_sum:.2f}")
    print(f"- Range IDs: Esperado 10000-10999, Obtido {min_id}-{max_id}")

    # Asserts
    integrity_passed = True
    if int(actual_rows) != num_rows:
        print("❌ FALHA: Contagem de linhas incorreta.")
        integrity_passed = False
    
    if abs(float(actual_freight_sum) - expected_freight_sum) > 0.01:
        print(f"❌ FALHA: Soma de valores (Integridade de Dados) incorreta. Diferença: {abs(float(actual_freight_sum) - expected_freight_sum)}")
        integrity_passed = False
        
    if int(min_id) != 10000 or int(max_id) != 10000 + num_rows - 1:
        print("❌ FALHA: Integridade dos IDs de registro falhou.")
        integrity_passed = False

    if integrity_passed:
        print("\n✅ TESTE DE INTEGRIDADE PASSOU!")
    else:
        print("\n❌ TESTE DE INTEGRIDADE FALHOU!")
    
    return integrity_passed

if __name__ == "__main__":
    test_data_integrity()
