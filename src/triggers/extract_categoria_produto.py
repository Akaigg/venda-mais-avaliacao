import logging
import azure.functions as func
import os
import pyodbc

bp = func.Blueprint()
@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_categoria_produto(myTimer: func.TimerRequest) -> None:

    sql_server = os.getenv('SQL_SERVER_SOURCE')
    sql_database = os.getenv('SQL_DATABASE_SOURCE')
    sql_user = os.getenv('SQL_USER_SOURCE')
    sql_pass = os.getenv('SQL_PASSWORD_SOURCE')


    connection_string = f'Driver={{ODBC Driver 17 for SQL Server}};Server:{sql_server};Database={sql_database};usuario={sql_user};senha={sql_pass}'

    try:
        conn = pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        logging.error(f"Erro na conexão: {e}")

    logging.info(f"""servidor: {sql_server}, banco: {sql_database}, usuario: {sql_user}, senha: {sql_pass}""")