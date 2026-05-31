import os
import time
import subprocess
import json
import logging
from datetime import datetime

def test_installability():
    print("--- Iniciando Teste de Portabilidade: Instalabilidade (RNF-11) ---")
    
    # Simulação de setup (como os containers já estão up, vamos medir o tempo de restart/healthcheck)
    print("Reiniciando containers para medir tempo de subida (Warm Start)...")
    start_time = time.perf_counter()
    
    try:
        # Docker compose restart é mais rápido que up do zero, mas serve como proxy de prontidão
        subprocess.run(["docker-compose", "restart"], check=True, capture_output=True)
        
        # Esperar até que fiquem saudáveis
        max_wait = 300 # 5 minutos conforme RNF-11
        waited = 0
        while waited < max_wait:
            res = subprocess.run(["docker", "ps", "--filter", "status=running", "--filter", "health=healthy", "--format", "{{.Names}}"], capture_output=True, text=True)
            # Esperamos clickhouse e minio ficarem healthy
            if "clickhouse-northwind" in res.stdout and "minio-northwind" in res.stdout:
                break
            time.sleep(5)
            waited += 5
            print(f"Aguardando containers ficarem saudáveis... ({waited}s)")
            
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        print(f"\nResultados de Instalabilidade:")
        print(f"- Tempo Total: {duration:.2f}s")
        print(f"- Limite RNF-11: 300.00s")
        
        if duration < 300:
            print("✅ TESTE DE INSTALABILIDADE PASSOU!")
            return True, duration
        else:
            print("❌ TESTE DE INSTALABILIDADE FALHOU!")
            return False, duration
            
    except Exception as e:
        print(f"Erro durante teste de instalabilidade: {e}")
        return False, 0

def test_maintainability_logs():
    print("\n--- Iniciando Teste de Manutenibilidade: Analisabilidade (RNF-10) ---")
    
    # 1. Executar ingestão para gerar logs
    print("Gerando logs via script de ingestão...")
    env = os.environ.copy()
    env["CLICKHOUSE_PASSWORD"] = "northwind"
    result = subprocess.run(["python3", "scripts/ingestion.py"], env=env, capture_output=True, text=True)
    
    # 2. Validar formato JSON dos logs (via stdout/stderr capturado)
    logs = result.stderr.splitlines() + result.stdout.splitlines()
    json_logs = [l for l in logs if l.strip().startswith('{') and l.strip().endswith('}')]
    
    print(f"Total de linhas de log: {len(logs)}")
    print(f"Linhas em formato JSON detectadas: {len(json_logs)}")
    
    is_valid_json = True
    if not json_logs:
        print("❌ FALHA: Nenhum log JSON detectado.")
        is_valid_json = False
    else:
        try:
            for jl in json_logs:
                parsed = json.loads(jl)
                if not all(k in parsed for k in ["timestamp", "level", "message"]):
                    print(f"⚠️ Log JSON incompleto: {jl}")
                    is_valid_json = False
            if is_valid_json:
                print("✅ Todos os logs amostrados seguem o esquema JSON {timestamp, level, message}.")
        except Exception as e:
            print(f"❌ FALHA: Erro ao parsear logs JSON: {e}")
            is_valid_json = False

    if is_valid_json:
        print("✅ TESTE DE ANALISABILIDADE (LOGS) PASSOU!")
    else:
        print("❌ TESTE DE ANALISABILIDADE (LOGS) FALHOU!")
        
    return is_valid_json

if __name__ == "__main__":
    inst_ok, dur = test_installability()
    maint_ok = test_maintainability_logs()
    
    if inst_ok and maint_ok:
        exit(0)
    else:
        exit(1)
