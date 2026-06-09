import logging
import azure.functions as func
import os
import time
import pyodbc
import pymssql

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_titulo_receber(myTimer: func.TimerRequest) -> None:
    sql_server = os.getenv("SQL_SERVER_SOURCE")
    sql_database = os.getenv("SQL_DATABASE_SOURCE")
    sql_user = os.getenv("SQL_USER_SOURCE")
    sql_pass = os.getenv("SQL_PASSWORD_SOURCE")
    
    # Query idêntica para o teste de volumetria
    query = "SELECT * FROM erp.titulo_receber"
    
    logging.info("--- POC ---")

    sql_driver = "ODBC Driver 18 for SQL Server"
    connection_string_odbc = (
        f"DRIVER={{{sql_driver}}};SERVER={sql_server};DATABASE={sql_database};"
        f"UID={sql_user};PWD={sql_pass};Encrypt=yes;TrustServerCertificate=yes;"
    )
    
    tempos_pyodbc = []
    qtd_registros_odbc = 0
    
    for i in range(1, 3):
        start_time = time.time()
        try:
            with pyodbc.connect(connection_string_odbc) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall() # Traz todas as linhas para a memória
                    qtd_registros_odbc = len(rows)
            end_time = time.time()
            exec_time = end_time - start_time
            tempos_pyodbc.append(exec_time)
            logging.info(f"[pyodbc] Execução {i}: {exec_time:.4f} segundos")
        except Exception as e:
            logging.error(f"[pyodbc] Erro na execução {i}: {str(e)}")
            
    media_pyodbc = sum(tempos_pyodbc) / len(tempos_pyodbc) if tempos_pyodbc else 0

    tempos_pymssql = []
    qtd_registros_mssql = 0
    
    for i in range(1, 3):
        start_time = time.time()
        try:
            with pymssql.connect(server=sql_server, user=sql_user, password=sql_pass, database=sql_database) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall() 
                    qtd_registros_mssql = len(rows)
            end_time = time.time()
            exec_time = end_time - start_time
            tempos_pymssql.append(exec_time)
            logging.info(f"[pymssql] Execução {i}: {exec_time:.4f} segundos")
        except Exception as e:
            logging.error(f"[pymssql] Erro na execução {i}: {str(e)}")
            
    media_pymssql = sum(tempos_pymssql) / len(tempos_pymssql) if tempos_pymssql else 0

    logging.info("--- RESULTADO FINAL DA POC ---")
    logging.info(f"Tabela testada: erp.titulo_receber (Registros: {qtd_registros_odbc})")
    logging.info(f"Tempo Médio pyodbc: {media_pyodbc:.4f} segundos")
    logging.info(f"Tempo Médio pymssql: {media_pymssql:.4f} segundos")
    logging.info("--------------------------------")