import logging
import azure.functions as func
import os
import pyodbc

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_categoria_produto(myTimer: func.TimerRequest) -> None:

    sql_server = os.getenv('SQL_SERVER_SOURCE')
    sql_database = os.getenv('SQL_DATABASE_SOURCE')
    sql_user = os.getenv('SQL_USER_SOURCE')
    sql_pass = os.getenv('SQL_PASSWORD_SOURCE')
    
    sql_driver = "ODBC Driver 18 for SQL Server"
    
    connection_string = (
        f"DRIVER={{{sql_driver}}};"
        f"SERVER={sql_server};"
        f"DATABASE={sql_database};"
        f"UID={sql_user};"
        f"PWD={sql_pass};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )

    logging.info("Buscando a lista de tabelas existentes no banco de dados...")
    
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if not rows:
                    logging.info("Nenhuma tabela foi encontrada neste banco de dados.")
                else:
                    logging.info(f"--- LISTA DE TABELAS ENCONTRADAS (Total: {len(rows)}) ---")
                    for row in rows:
                        logging.info(f"Tabela disponível: {row[0]}.{row[1]}")
                    logging.info("--------------------------------------------------")
                
    except Exception as e:
        logging.error(f"Erro ao mapear as tabelas: {str(e)}")