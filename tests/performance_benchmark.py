import os
import time
import psutil
import subprocess
import threading
import json
from datetime import datetime

def monitor_resources(process_pid, interval=0.1, results=[]):
    try:
        proc = psutil.Process(process_pid)
        while proc.is_running():
            try:
                mem = proc.memory_info().rss / (1024 * 1024)  # MB
                cpu = proc.cpu_percent(interval=None)
                results.append({"time": time.time(), "mem_mb": mem, "cpu_pct": cpu})
                time.sleep(interval)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
    except psutil.NoSuchProcess:
        pass

def run_benchmark(num_rows):
    # 1. Gerar dados
    data_dir = f"dados_perf_{num_rows}"
    csv_path = os.path.join(data_dir, "orders_perf.csv")
    print(f"\n--- Iniciando Benchmark para {num_rows} linhas ---")
    subprocess.run(["python3", "tests/generate_performance_data.py", str(num_rows), csv_path], check=True)
    
    # 2. Configurar ambiente
    env = os.environ.copy()
    env["CSV_DATA_DIR"] = data_dir
    
    # 3. Executar ingestão e monitorar
    start_time = time.perf_counter()
    
    # Usando subprocess.Popen para capturar o PID
    p = subprocess.Popen(["python3", "scripts/ingestion.py"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    monitor_results = []
    monitor_thread = threading.Thread(target=monitor_resources, args=(p.pid, 0.2, monitor_results))
    monitor_thread.start()
    
    stdout, stderr = p.communicate()
    end_time = time.perf_counter()
    monitor_thread.join()
    
    duration = end_time - start_time
    throughput = num_rows / duration if duration > 0 else 0
    
    max_mem = max([r["mem_mb"] for r in monitor_results]) if monitor_results else 0
    avg_cpu = sum([r["cpu_pct"] for r in monitor_results]) / len(monitor_results) if monitor_results else 0
    
    print(f"Duração: {duration:.2f}s")
    print(f"Throughput: {throughput:.2f} linhas/s")
    print(f"Pico de Memória: {max_mem:.2f} MB")
    print(f"CPU Média: {avg_cpu:.2f}%")
    
    # Limpeza
    # subprocess.run(["rm", "-rf", data_dir])
    
    return {
        "rows": num_rows,
        "duration": duration,
        "throughput": throughput,
        "max_mem_mb": max_mem,
        "avg_cpu_pct": avg_cpu,
        "success": p.returncode == 0
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        scenarios = [int(x) for x in sys.argv[1:]]
    else:
        scenarios = [100000, 300000, 500000] # Load, Stress, Scaling
    
    all_results = []
    
    for s in scenarios:
        res = run_benchmark(s)
        all_results.append(res)
    
    with open("performance_results.json", "w") as f:
        json.dump(all_results, f, indent=4)
    
    print("\nResultados salvos em performance_results.json")
