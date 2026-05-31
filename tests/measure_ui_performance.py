import time
import requests

def measure_ui_load(url, iterations=5):
    times = []
    print(f"Medindo tempo de resposta da UI em {url}...")
    for i in range(iterations):
        start = time.perf_counter()
        try:
            r = requests.get(url)
            r.raise_for_status()
            end = time.perf_counter()
            times.append(end - start)
            print(f"Iteração {i+1}: {(end - start)*1000:.2f} ms")
        except Exception as e:
            print(f"Erro na iteração {i+1}: {e}")
        time.sleep(1)
    
    if times:
        avg = sum(times) / len(times)
        print(f"\nTempo Médio de Resposta: {avg*1000:.2f} ms")
        return avg
    return None

if __name__ == "__main__":
    measure_ui_load("http://localhost:8501")
