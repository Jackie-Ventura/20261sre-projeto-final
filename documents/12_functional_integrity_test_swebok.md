# Relatório de Teste de Adequação Funcional: Integridade de Dados (SWEBOK 4.0)

## 1. Introdução
Este teste avalia o atributo de qualidade **Adequação Funcional**, especificamente o sub-atributo **Integridade**, conforme definido na **ISO 25010** e no **SWEBOK 4.0 (Capítulo 4)**.

O objetivo é garantir que os dados processados pelo pipeline de ingestão sejam transferidos do CSV para o ClickHouse sem perdas, duplicações não intencionais ou corrupção de valores.

## 2. Metodologia de Teste (SWEBOK 4.0)
Seguindo as práticas de **Functional Testing** e **Data Integrity Testing**, foi realizado um teste de ponta a ponta (E2E):
1.  **Geração de Massa Controlada:** Criação de um CSV com 1.000 registros, contendo valores numéricos (`freight`) calculados de forma determinística.
2.  **Cálculo de Base (Golden Record):** Cálculo prévio da soma total dos valores e contagem de registros.
3.  **Execução do Pipeline:** Ingestão dos dados via `scripts/ingestion.py`.
4.  **Reconciliação Automática:** Consulta ao ClickHouse utilizando funções de extração JSON (`JSONExtractFloat`, `JSONExtractInt`) para validar os dados persistidos.

## 3. Resultados do Teste de Integridade

| Métrica | Valor Esperado (CSV) | Valor Obtido (ClickHouse) | Diferença | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Contagem de Linhas** | 1.000 | 1.000 | 0 | ✅ PASS |
| **Soma Total (Freight)** | 5.255.250,00 | 5.255.250,00 | 0.00 | ✅ PASS |
| **Mínimo Order ID** | 10.000 | 10.000 | 0 | ✅ PASS |
| **Máximo Order ID** | 10.999 | 10.999 | 0 | ✅ PASS |

## 4. Conclusão Técnica
O teste de adequação funcional confirmou que o sistema cumpre o requisito **RNF-01 (Completude)**. 

### Observações:
- **Transformação Segura:** O uso de DuckDB para converter CSV em JSON e a inserção via `clickhouse-connect` preservaram a precisão decimal dos valores.
- **Rastreabilidade:** O uso da coluna `tag` permitiu filtrar e isolar os dados do teste, garantindo que a reconciliação fosse precisa mesmo em um ambiente compartilhado.
- **Robustez:** O sistema tratou corretamente a carga total, sem falhas de conexão ou perda de pacotes durante a inserção em chunks.

**Data do Teste:** 31 de Maio de 2026
**Responsável:** Gemini CLI (Auto-Edit Mode)
