import os
import time
import subprocess
import json
import logging
from datetime import datetime

# Configuração de logging para capturar o tempo
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_retry_mechanism():
    print("--- Iniciando Teste de Resiliência: Mecanismo de Retry ---")
    
    # Configurar ambiente com host inválido para forçar falha e retry
    env = os.environ.copy()
    env["CLICKHOUSE_HOST"] = "host_inexistente_de_teste"
    env["CLICKHOUSE_PORT"] = "8123"
    
    start_time = time.perf_counter()
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando ingestão com host inválido (esperando 5 tentativas)...")
    
    # Executar a ingestão
    process = subprocess.Popen(
        ["python3", "scripts/ingestion.py"], 
        env=env, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        text=True
    )
    
    stdout, stderr = process.communicate()
    end_time = time.perf_counter()
    
    duration = end_time - start_time
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processo finalizado.")
    
    # Analisar logs de stderr (onde o tenacity/logging joga as tentativas)
    retry_count = stderr.count("Tentando conectar ao ClickHouse")
    
    print(f"\nResultados:")
    print(f"- Duração total: {duration:.2f}s")
    print(f"- Tentativas detectadas: {retry_count}")
    
    # O backoff é: min 2s, max 10s, mult 1. 
    # Tentativa 1: imediata
    # Tentativa 2: +2s
    # Tentativa 3: +4s
    # Tentativa 4: +8s
    # Tentativa 5: +10s (max)
    # Total esperado: ~24s + tempo de timeout de rede
    
    resilience_passed = True
    if retry_count != 5:
        print(f"❌ FALHA: Esperava 5 tentativas, mas detectei {retry_count}.")
        resilience_passed = False
    
    if duration < 15:
        print(f"❌ FALHA: O tempo de execução ({duration:.2f}s) foi menor que o esperado para o backoff exponencial.")
        resilience_passed = False
    
    if "Falha crítica no pipeline de ingestão" in stderr:
        print("✅ Falha crítica capturada corretamente após exaustão de retries.")
    else:
        print("❌ FALHA: Mensagem de falha crítica não encontrada nos logs.")
        resilience_passed = False

    if resilience_passed:
        print("\n✅ TESTE DE RESILIÊNCIA PASSOU!")
    else:
        print("\n❌ TESTE DE RESILIÊNCIA FALHOU!")
        
    return resilience_passed

def check_container_health():
    print("\n--- Verificando Saúde dos Containers (Healthchecks) ---")
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}: {{.Status}}"], 
            capture_output=True, 
            text=True
        )
        print(result.stdout)
        
        if "healthy" in result.stdout:
            print("✅ Containers estão saudáveis e reportando status corretamente.")
            return True
        else:
            print("⚠️ Alguns containers podem não estar saudáveis ou não possuem healthcheck.")
            return False
    except Exception as e:
        print(f"Erro ao verificar containers: {e}")
        return False

if __name__ == "__main__":
    retry_ok = test_retry_mechanism()
    health_ok = check_container_health()
    
    if retry_ok and health_ok:
        exit(0)
    else:
        exit(1)
