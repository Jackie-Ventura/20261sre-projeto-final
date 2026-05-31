# Relatório de Teste de Eficiência de Desempenho (SWEBOK 4.0)

## 1. Introdução
Este teste avalia o atributo de qualidade **Eficiência de Desempenho** do pipeline Northwind, seguindo as diretrizes do **SWEBOK 4.0 (Capítulo 4: Software Testing)** e **ISO 25010**.

O objetivo é medir a capacidade do sistema em processar grandes volumes de dados (ingestão) e responder a consultas (dashboard) utilizando recursos de forma otimizada.

## 2. Metodologia (SWEBOK 4.0)
Foram aplicados três tipos de testes de performance:
- **Load Testing:** Avaliação sob carga nominal (100.000 registros).
- **Stress Testing:** Avaliação nos limites e além da carga nominal (500.000 registros).
- **Scalability Testing:** Avaliação da tendência de performance com o aumento massivo de dados (1.000.000 registros).

### Métricas Coletadas:
- **Tempo de Resposta/Duração:** Tempo total para completar a tarefa.
- **Throughput:** Registros processados por segundo.
- **Utilização de Recursos:** Pico de memória RAM (RSS) e uso médio de CPU.

## 3. Resultados dos Testes

### 3.1 Ingestão (ETL Pipeline)
O processamento foi realizado utilizando a arquitetura DuckDB + ClickHouse com processamento em *chunks*.

| Cenário | Qtd. Linhas | Duração | Throughput | Pico RAM | CPU Média | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Load** | 100.000 | 6.47s | 15.459/s | 214 MB | 25.7% | ✅ PASS |
| **Stress** | 500.000 | 22.09s | 22.635/s | 270 MB | 18.2% | ✅ PASS |
| **Scaling** | 1.000.000 | 43.80s | 22.828/s | 300 MB | 16.7% | ✅ PASS |

### 3.2 Interface (Strategic Dashboard)
Medição do tempo de resposta da UI Streamlit (First Contentful Paint/Request-Response).

| Métrica | Objetivo | Resultado | Status |
| :--- | :--- | :--- | :--- |
| Tempo de Resposta Médio | < 5.000 ms | 48.80 ms | ✅ PASS |
| Tempo de Resposta (Pico) | < 5.000 ms | 212.68 ms | ✅ PASS |

## 4. Análise Técnica e Conformidade
1.  **Eficiência de Tempo (RNF-02):** O requisito era < 60s para 100k linhas. O sistema entregou em **~6.5s**, sendo 9x mais rápido que o esperado.
2.  **Utilização de Recursos (RNF-03):** O limite era 1GB de RAM. Mesmo com 1 milhão de linhas, o consumo máximo foi de **300MB**, demonstrando a eficácia do processamento por *chunks*.
3.  **Escalabilidade:** O throughput aumentou e estabilizou conforme o volume cresceu, indicando que o sistema possui baixo *overhead* inicial e escala linearmente.

## 5. Conclusão
O sistema Northwind Modern Data Stack demonstra alta eficiência de desempenho. A escolha de ferramentas como **DuckDB** para transformação local e **ClickHouse** para armazenamento colunar, aliada à estratégia de **ingestão em chunks**, garantiu que os limites de tempo e memória fossem respeitados com ampla margem de segurança.

**Data do Teste:** 31 de Maio de 2026
**Responsável:** Gemini CLI (Auto-Edit Mode)
