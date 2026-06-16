import logging
import azure.functions as func
import os
import pyodbc

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_titulo_receber(myTimer: func.TimerRequest) -> None:
    logging.info("=== iniciando pipeline ===")

    sql_server_source = os.getenv("SQL_SERVER_SOURCE")
    sql_database_source = os.getenv("SQL_DATABASE_SOURCE")
    sql_user_source = os.getenv("SQL_USER_SOURCE")
    sql_pass_source = os.getenv("SQL_PASSWORD_SOURCE")
    sql_driver = "ODBC Driver 18 for SQL Server"
    
    connection_source = (
        f"DRIVER={{{sql_driver}}};SERVER={sql_server_source};DATABASE={sql_database_source};"
        f"UID={sql_user_source};PWD={sql_pass_source};Encrypt=yes;TrustServerCertificate=yes;"
    )

    sql_server_dest = os.getenv("SQL_SERVER_DESTINATION")
    sql_database_dest = os.getenv("SQL_DATABASE_DESTINATION")
    sql_user_dest = os.getenv("SQL_USER_DESTINATION")
    sql_pass_dest = os.getenv("SQL_PASSWORD_DESTINATION")
    
    connection_destination = (
        f"DRIVER={{{sql_driver}}};SERVER={sql_server_dest};DATABASE={sql_database_dest};"
        f"UID={sql_user_dest};PWD={sql_pass_dest};Encrypt=yes;TrustServerCertificate=yes;"
    )

    query_extract = "SELECT * FROM dbo.titulo_receber"

    try:
        logging.info("Conectando ao banco de dados do professor (Origem)...")
        with pyodbc.connect(connection_source) as conn_source:
            with conn_source.cursor() as cursor_source:
                
                logging.info("Extraindo dados de dbo.titulo_receber...")
                cursor_source.execute(query_extract)
                rows = cursor_source.fetchall()
                
                if not rows:
                    logging.info("Nenhum dado encontrado.")
                    return
                
                num_columns = len(cursor_source.description)
                logging.info(f"Sucesso! {len(rows)} registros e {num_columns} colunas extraídos.")

        logging.info("Conectando ao nosso banco de dados (Destino)...")
        with pyodbc.connect(connection_destination) as conn_dest:
            with conn_dest.cursor() as cursor_dest:
                
                logging.info("Limpando dados antigos da sua tabela (Truncate)...")
                cursor_dest.execute("TRUNCATE TABLE dbo.titulo_receber")
                
                placeholders = ", ".join(["?"] * num_columns)
                query_load = f"INSERT INTO dbo.titulo_receber VALUES ({placeholders})"
                
                logging.info("Inserindo")
                cursor_dest.executemany(query_load, rows)
                
                conn_dest.commit()
                
        logging.info("=== pipeline atualizado ===")

    except Exception as e:
        logging.error(f"Erro: {str(e)}")