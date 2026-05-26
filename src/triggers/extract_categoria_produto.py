import logging
import azure.functions as func
import os
import pyodbc

bp = func.Blueprint()
@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_categoria_produto(myTimer: func.TimerRequest) -> None:

    sql_server = 'SQL_SERVER_SOURCE'
    sql_database = 'SQL_DATABASE_SOURCE'
    sql_user = 'SQL_USER_SOURCE'
    sql_pass = 'SQL_PASSWORD_SOURCE'

    logging.info(f"""servidor: {sql_server}, banco: {sql_database}, usuario: {sql_user}, senha: {sql_pass}""")