import os
import duckdb
import clickhouse_connect
from dotenv import load_dotenv
import time
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configuração de Logging conforme RNF-10 (Wave 2.2)
import json

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage()
        }
        return json.dumps(log_record)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter(datefmt='%Y-%m-%d %H:%M:%S'))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False

load_dotenv()

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Exception)),
    reraise=True
)
def get_clickhouse_client():
    ch_host = os.getenv("CLICKHOUSE_HOST", "localhost")
    ch_port = int(os.getenv("CLICKHOUSE_PORT", 8123))
    ch_user = os.getenv("CLICKHOUSE_USER", "default")
    ch_pass = os.getenv("CLICKHOUSE_PASSWORD", "")
    
    logger.info(f"Tentando conectar ao ClickHouse em {ch_host}:{ch_port}")
    client = clickhouse_connect.get_client(host=ch_host, port=ch_port, username=ch_user, password=ch_pass)
    client.command("SELECT 1") # Heartbeat (Tarefa 2.3)
    return client

def validate_csv(file_path):
    """Tarefa 1.3: Validar integridade básica do CSV."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
    if os.path.getsize(file_path) == 0:
        raise ValueError(f"Arquivo vazio: {file_path}")
    return True

def run_ingestion():
    ch_db = os.getenv("CLICKHOUSE_DB", "northwind")
    csv_dir = os.getenv("CSV_DATA_DIR", "dados_northwind")
    
    try:
        # Cliente ClickHouse com Retry e Heartbeat
        client = get_clickhouse_client()
        
        # Inicializar DuckDB
        con = duckdb.connect(database=':memory:')

        logger.info(f"Iniciando ingestão de CSVs (modo Chunked) para a tabela {ch_db}.ingestion...")

        if not os.path.exists(csv_dir):
            logger.error(f"Diretório de CSVs não encontrado: {csv_dir}")
            return

        for file_name in os.listdir(csv_dir):
            if file_name.endswith(".csv"):
                file_path = os.path.join(csv_dir, file_name)
                
                try:
                    # Validação (Tarefa 1.3)
                    validate_csv(file_path)
                    logger.info(f"Processando arquivo em chunks: {file_name}")

                    # Transformação via DuckDB - Tarefa 2.1 (Performance)
                    query = f"""
                        SELECT 
                            current_timestamp as ingestion_timestamp,
                            CAST(to_json(t) AS TEXT) as data,
                            '{file_name}' as tag
                        FROM read_csv_auto('{file_path}') t
                    """
                    
                    # Convertendo para Relation para processamento em chunks
                    rel = con.sql(query)
                    
                    total_rows = 0
                    while True:
                        # fetch_df_chunk() retorna um DataFrame por vez, respeitando a memória
                        df_chunk = rel.fetch_df_chunk()
                        if df_chunk is None or len(df_chunk) == 0:
                            break
                        
                        client.insert_df(f"{ch_db}.ingestion", df_chunk)
                        total_rows += len(df_chunk)
                        logger.info(f"Chunk processado: {len(df_chunk)} linhas (Total: {total_rows})")
                    
                    logger.info(f"Sucesso: Ingestão de {file_name} finalizada com {total_rows} linhas.")
                
                except Exception as e:
                    # Tratamento de Exceção Robusto (Tarefa 1.2)
                    logger.error(f"Erro ao processar {file_name}: {str(e)}")

        logger.info("Ingestão concluída!")

    except Exception as e:
        logger.critical(f"Falha crítica no pipeline de ingestão: {str(e)}")

if __name__ == "__main__":
    run_ingestion()
