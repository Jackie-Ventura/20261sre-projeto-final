# Plano de Teste de Modelagem de Dados

Este documento descreve os testes realizados para validar a integridade e a qualidade dos modelos de dados dbt nas camadas Silver e Gold.

## 1. Objetivos do Teste
- Garantir a unicidade das chaves primárias.
- Validar a obrigatoriedade de campos críticos (not null).
- Garantir a consistência das transformações entre as camadas Medallion.

## 2. Modelos Testados
- `stg_orders` (Silver): Limpeza e tipagem de pedidos.
- `stg_order_details` (Silver): Limpeza e cálculo de totais por item.
- `fct_sales` (Gold): Visão agregada de vendas para o dashboard.

## 3. Metodologia (dbt Testing)
Foram implementados testes genéricos no arquivo `schema.yml` para cada modelo:
- **Unique:** Verifica se há valores duplicados na coluna.
- **Not Null:** Verifica se há valores nulos em colunas obrigatórias.

## 4. Resultados dos Testes (Executados em 31/05/2026)

| Modelo | Teste | Coluna | Resultado | Status |
| :--- | :--- | :--- | :--- | :--- |
| `stg_orders` | Unique | `order_id` | 0 falhas | ✅ PASS |
| `stg_orders` | Not Null | `order_id` | 0 falhas | ✅ PASS |
| `stg_orders` | Not Null | `customer_id` | 0 falhas | ✅ PASS |
| `stg_order_details`| Not Null | `order_id` | 0 falhas | ✅ PASS |
| `stg_order_details`| Not Null | `product_id`| 0 falhas | ✅ PASS |
| `fct_sales` | Not Null | `order_id` | 0 falhas | ✅ PASS |
| `fct_sales` | Not Null | `order_total_value`| 0 falhas | ✅ PASS |
| `fct_sales` | Not Null | `total_items` | 0 falhas | ✅ PASS |

## 5. Conclusão
A modelagem de dados está íntegra. Os testes confirmam que não há duplicidade de pedidos na camada Silver e que todos os KPIs fundamentais para o dashboard (valor total e itens) estão preenchidos na camada Gold.
