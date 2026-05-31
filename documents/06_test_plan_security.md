# Plano de Teste de Segurança

Este documento detalha o plano e os resultados dos testes de segurança realizados no pipeline Northwind, seguindo as diretrizes do **SWEBOK 4.0** e **ISO 25010**.

## 1. Objetivos do Teste
- Validar a **Confidencialidade** (RNF-08): Garantir que segredos e credenciais não estejam expostos.
- Validar a **Integridade** (RNF-09): Garantir que os arquivos de entrada não sejam corrompidos ou alterados.

## 2. Escopo do Teste
- Análise estática do código-fonte (SAST).
- Verificação de configuração de variáveis de ambiente.
- Auditoria de logs de execução.
- Verificação de checksums de arquivos de dados.

## 3. Ferramentas Utilizadas
- `detect-secrets`: Para scan de segredos.
- `hashlib (SHA-256)`: Para validação de integridade.
- `grep/Manual Review`: Para auditoria de logs.

## 4. Resultados dos Testes (Executados em 31/05/2026)

### 4.1 Confidencialidade
| Verificação | Resultado | Status |
| :--- | :--- | :--- |
| Scan de Segredos | 0 credenciais reais encontradas no código. | ✅ PASS |
| Uso de .env | Todas as senhas carregadas via `os.getenv`. | ✅ PASS |
| Exposição em Logs | Scripts de ingestão utilizam formatadores que protegem strings sensíveis. | ✅ PASS |

### 4.2 Integridade
| Verificação | Resultado | Status |
| :--- | :--- | :--- |
| Checksum SHA-256 | Implementado e validado para `northwind_orders.csv`. | ✅ PASS |
| Permissões .env | Identificada permissão `0666` (Recomendado: `0600`). | ⚠️ AVISO |

## 5. Conclusão
O sistema cumpre os requisitos de segurança para o ambiente de desenvolvimento. A principal recomendação é o ajuste de permissões de arquivos sensíveis em produção e o uso de conexões seguras (HTTPS/TLS) para o banco de dados.
