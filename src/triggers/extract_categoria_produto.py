import logging
import azure.functions as func
import os
import pymssql

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_categoria_produto(myTimer: func.TimerRequest) -> None:
    logging.info("Iniciando EL: dbo.categoria_produto")

    sql_server_source = os.getenv("SQL_SERVER_SOURCE")
    sql_database_source = os.getenv("SQL_DATABASE_SOURCE")
    sql_user_source = os.getenv("SQL_USER_SOURCE")
    sql_pass_source = os.getenv("SQL_PASSWORD_SOURCE")

    sql_server_dest = os.getenv("SQL_SERVER_DESTINATION")
    sql_database_dest = os.getenv("SQL_DATABASE_DESTINATION")
    sql_user_dest = os.getenv("SQL_USER_DESTINATION")
    sql_pass_dest = os.getenv("SQL_PASSWORD_DESTINATION")

    colunas_sem_id = (
        "cd_categoria, nm_categoria, fl_ativo, dt_inclusao, "
        "dt_atualizacao, nm_sistema_origem, cd_registro_origem"
    )
    
    query_extract = f"SELECT {colunas_sem_id} FROM [dbo].[categoria_produto]"
    query_load = f"INSERT INTO [dbo].[categoria_produto] ({colunas_sem_id}) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    try:
        logging.info("Conectando na Origem...")
        with pymssql.connect(server=sql_server_source, user=sql_user_source, password=sql_pass_source, database=sql_database_source) as conn_source:
            with conn_source.cursor() as cursor_source:
                cursor_source.execute(query_extract)
                rows = cursor_source.fetchall()
                
                if not rows:
                    logging.info("Origem vazia.")
                    return
                
                logging.info(f"{len(rows)} registros extraídos.")

        logging.info("Conectando no Destino...")
        with pymssql.connect(server=sql_server_dest, user=sql_user_dest, password=sql_pass_dest, database=sql_database_dest) as conn_dest:
            with conn_dest.cursor() as cursor_dest:
                cursor_dest.execute("TRUNCATE TABLE [dbo].[categoria_produto]")
                cursor_dest.executemany(query_load, rows)
                conn_dest.commit()
                
        logging.info("Pipeline executada com sucesso.")

    except Exception as e:
        logging.error(f"Erro na pipeline: {str(e)}")