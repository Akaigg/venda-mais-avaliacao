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
    )

    logging.info(f"Iniciando tentativa de conexão no banco: {sql_database}")
    
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                logging.info("Sucesso! Conexão estabelecida com pyodbc na Azure.")             
    except Exception as e:
        logging.error(f"Erro ao conectar com o banco de dados via pyodbc: {str(e)}")