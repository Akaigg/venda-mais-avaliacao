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

    logging.info(f"Iniciando consulta SELECT na tabela erp.categoria_produto...")
    
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                
                query = "SELECT TOP 10 * FROM erp.categoria_produto" 
                cursor.execute(query)
                
                rows = cursor.fetchall()
                
                if not rows:
                    logging.info("A tabela erp.categoria_produto está vazia.")
                else:
                    logging.info(f"Quantidade de registros encontrados: {len(rows)}")
                    for row in rows:
                        logging.info(f"Registro encontrado: {list(row)}")
                        
                logging.info("Extração de teste concluída com sucesso!")
                
    except Exception as e:
        logging.error(f"Erro ao executar o SELECT na tabela erp.categoria_produto: {str(e)}")