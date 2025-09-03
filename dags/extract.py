"""
Pipeline de Extração de dados, oriundos de arquivos CSV e Conexão com Banco de 
Dados Postgres de origem. 

Essa Dag realiza extrações de dados de algumas tabelas Postgres e de um arquivo
CSV, que armazena transações de clientes registradas.

Após a extração dos dados, é realizado um load dos dados para um Data Warehouse 
containerizado, onde é criado as tabelas tanto dos dados do Postgres quanto uma
tabelas "transacoes", para representar o arquivo CSV.
"""

from airflow.decorators import dag, task 
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime 
import os 
from typing import List
import pandas as pd

# Constantes da aplicação - criadas para facilitar a utilização de caminhos e 
# tabelas durante o uso das Dags.
CSV_SOURCE_PATH: str = '/usr/local/airflow/include/transacoes.csv'
DATALAKE_PATH: str = '/usr/local/airflow/include/datalake'
SOURCE_TABLES: List[str] = [
    "agencias",
    "clientes", 
    "colaborador_agencia",
    "colaboradores",
    "contas",
    "propostas_credito"
]

# Constantes de conexões cadastradas pela interface do Airflow
SOURCE_DB_CONN_ID: str = "db_origem"
DW_DB_CONN_ID: str = "db_datawarehouse"


@dag(
    dag_id="pipeline_extraction",
    schedule='35 4 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["pipeline_extract", "extract", "sql", "csv"],
)
def pipeline_extraction() -> None:
    """
    Pipeline do sistema que orquestra toda a extração e carga dos dados para o
    datawarehouse.
    
    Nela são divididas as tasks de extração do postgres e csv, e carga no banco
    de dados de origem, que também é um postgres.
    Necessário configurar as conexões pela interface do airflow antes de rodar
    as dags.
    """
    
    @task()
    def postgres_extract() -> None:
        """
        Extração dos dados do PostgresSQL, nomeado de banvic-db no arquivo do 
        docker compose. 
        
        As tabelas de extração são: agencias, clientes, colaborador_agencia,
        colaboradores, contas e propostas_credito.
        """
        try:
            pg_connection = PostgresHook(postgres_conn_id=SOURCE_DB_CONN_ID)
            
            os.makedirs(DATALAKE_PATH, exist_ok=True)
            
            for table_name in SOURCE_TABLES:
                sql_query = f"SELECT * FROM {table_name}"
                df = pg_connection.get_pandas_df(sql_query)
                
                output_filename = f"{datetime.now():%Y-%m-%d}_sql_{table_name}.csv"
                output_path = os.path.join(DATALAKE_PATH, output_filename)
                
                df.to_csv(
                    output_path,
                    header=True,
                    index=False,
                    quoting=1
                )
                
        except Exception as e:
            print(f"Erro ao tentar extrair dados do Postgres: {str(e)}")
            raise
    
    @task()
    def extract_csv() -> None:
        """
        
        Extração dos dados do arquivo CSV.
        
        """
        try:
            df = pd.read_csv(CSV_SOURCE_PATH, sep=",")
            
            os.makedirs(DATALAKE_PATH, exist_ok=True)
            
            output_filename = f"{datetime.now():%Y-%m-%d}_csv_transacoes.csv"
            output_path = os.path.join(DATALAKE_PATH, output_filename)
            
            df.to_csv(
                output_path,
                header=True,
                index=False,
                quoting=1
            )
            
        except Exception as e:
            print(f"Erro ao tentar extrair dados do CSV: {str(e)}")
            raise

    @task()
    def load_dw() -> None:
        """
        Após todo o processo de extração, e se todas as duas tasks forem 
        concluidas com sucesso, essa task é responsável por carregar os dados
        extraídos para o data warehouse.
        
        """
        try:
            pg_connection_dw = PostgresHook(postgres_conn_id=DW_DB_CONN_ID)
            engine = pg_connection_dw.get_sqlalchemy_engine()
            
            csv_files = [f for f in os.listdir(DATALAKE_PATH) if f.endswith(".csv")]
            
            for filename in csv_files:
                file_path = os.path.join(DATALAKE_PATH, filename)
                df = pd.read_csv(file_path, sep=",")
                table_name = os.path.splitext(filename.split('_')[2])[0]
                
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='replace',
                    index=False
                )
                
        except Exception as e:
            print(f"Erro ao carregar o Data Warehouse: {str(e)}")
            raise


    csv_task = extract_csv()
    postgres_task = postgres_extract()
    load_task = load_dw()

    [csv_task, postgres_task] >> load_task


pipeline_extraction()