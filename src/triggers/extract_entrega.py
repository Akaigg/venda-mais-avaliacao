import logging
import azure.functions as func
import os
from sqlalchemy import create_engine, text

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_cliente_sqlalchemy(myTimer: func.TimerRequest) -> None: 

    sql_server = os.getenv('SQL_SERVER_SOURCE')
    sql_database = os.getenv('SQL_DATABASE_SOURCE')
    sql_user = os.getenv('SQL_USER_SOURCE')
    sql_pass = os.getenv('SQL_PASSWORD_SOURCE')
    sql_driver = "ODBC Driver 18 for SQL Server"
    
    connection_url = (
        f"mssql+pyodbc://{sql_user}:{sql_pass}@{sql_server}/{sql_database}"
        f"?driver={sql_driver}&Encrypt=yes&TrustServerCertificate=ye"
    )

    logging.info("Iniciando conexão com SQLAlchemy na tabela erp.cliente...")
    
    try:
        engine = create_engine(connection_url)
        
        with engine.connect() as conn:
            query = text("SELECT TOP 10 * FROM erp.cliente")
            result = conn.execute(query)
            rows = result.fetchall()
            
            if not rows:
                logging.info("A tabela erp.cliente está vazia.")
            else:
                logging.info(f"Quantidade de registros encontrados: {len(rows)}")
                for row in rows:
                    logging.info(f"Cliente: {list(row)}")
                    
            logging.info("Extração de clientes via SQLAlchemy concluída!")
            
    except Exception as e:
        logging.error(f"Erro ao executar o SELECT via SQLAlchemy: {str(e)}")