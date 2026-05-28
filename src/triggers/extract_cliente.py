import logging
import azure.functions as func
import os
import pymssql

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_cliente(myTimer: func.TimerRequest) -> None:

    sql_server = os.getenv('SQL_SERVER_SOURCE')
    sql_database = os.getenv('SQL_DATABASE_SOURCE')
    sql_user = os.getenv('SQL_USER_SOURCE')
    sql_pass = os.getenv('SQL_PASSWORD_SOURCE')

    logging.info(f"Iniciando consulta SELECT na tabela erp.cliente usando pymssql...")
    
    try:
        with pymssql.connect(server=sql_server, user=sql_user, password=sql_pass, database=sql_database) as conn:
            with conn.cursor() as cursor:
                
                query = "SELECT TOP 10 * FROM erp.cliente" 
                cursor.execute(query)
                
                rows = cursor.fetchall()
                
                if not rows:
                    logging.info("A tabela erp.cliente está vazia.")
                else:
                    logging.info(f"Quantidade de registros encontrados: {len(rows)}")
                    
                    for row in rows:
                        logging.info(f"Cliente encontrado: {list(row)}")
                        
                logging.info("Extração de clientes finalizada com sucesso!")
                
    except Exception as e:
        logging.error(f"Erro ao executar o SELECT na tabela erp.cliente via pymssql: {str(e)}")
