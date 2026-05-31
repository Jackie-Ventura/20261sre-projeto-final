# Relatório de Teste de Confiabilidade e Resiliência (SWEBOK 4.0)

## 1. Introdução
Este relatório avalia os atributos de **Confiabilidade** e **Resiliência** do sistema Northwind, baseando-se nas diretrizes do **SWEBOK 4.0 (Software Testing)** e **ISO 25010**.

O foco é a capacidade do sistema de se recuperar de falhas transitórias de rede e manter a disponibilidade dos serviços essenciais.

## 2. Metodologia (SWEBOK 4.0)
Foram aplicadas técnicas de **Fault Injection** e **Availability Monitoring**:
- **Teste de Tolerância a Falhas:** Injeção de uma falha de DNS (host inválido) para validar se o pipeline de ingestão realiza retentativas automáticas.
- **Análise de Recuperabilidade:** Verificação do algoritmo de *Exponential Backoff* para garantir que o sistema não sobrecarregue o banco de dados durante falhas.
- **Monitoramento de Disponibilidade:** Verificação do status de saúde (*Healthchecks*) dos containers orchestrados via Docker Compose.

## 3. Resultados dos Testes

### 3.1 Tolerância a Falhas (RNF-07)
O mecanismo de retry foi testado forçando uma falha de conexão inicial.

| Métrica | Valor Esperado | Valor Obtido | Status |
| :--- | :--- | :--- | :--- |
| **Qtd. de Retentativas** | 5 | 5 | ✅ PASS |
| **Algoritmo de Espera** | Exponencial (min 2s) | Validado (Duração ~16.5s) | ✅ PASS |
| **Tratamento de Exceção** | Falha Crítica Logada | "Falha crítica no pipeline..." | ✅ PASS |

### 3.2 Disponibilidade (RNF-06)
Verificação do estado atual dos serviços em execução.

| Container | Mecanismo | Status Reportado | Status |
| :--- | :--- | :--- | :--- |
| **ClickHouse** | HTTP /ping | `healthy` | ✅ PASS |
| **MinIO** | /minio/health/live | `healthy` | ✅ PASS |
| **Dashboard** | Streamlit Process | `Up` | ✅ PASS |

## 4. Análise Técnica
1.  **Resiliência Robusta:** O uso da biblioteca `tenacity` com decoradores `@retry` provou ser eficaz. O sistema respeitou os intervalos de espera (2s, 4s, 8s...), o que evita o fenômeno de "Thundering Herd" em casos de queda massiva do banco de dados.
2.  **Auto-Cura (Self-Healing):** Os healthchecks definidos no `docker-compose.yml` permitem que a infraestrutura detecte e reinicie serviços instáveis automaticamente, garantindo a alta disponibilidade (RNF-06).

## 5. Conclusão
O sistema Northwind demonstra alta resiliência a falhas de rede. O pipeline de ingestão é capaz de tolerar instabilidades temporárias no banco de dados, e a infraestrutura de containers fornece as garantias necessárias para manter o sistema disponível.

**Data do Teste:** 31 de Maio de 2026
**Responsável:** Gemini CLI (Auto-Edit Mode)
