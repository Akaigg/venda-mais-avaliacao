import logging
import azure.functions as func
import os
import pymssql

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_titulo_receber(myTimer: func.TimerRequest) -> None:
    logging.info("=== INICIANDO PIPELINE EL COM PYMSSQL: dbo.titulo_receber ===")

    sql_server_source = os.getenv("SQL_SERVER_SOURCE")
    sql_database_source = os.getenv("SQL_DATABASE_SOURCE")
    sql_user_source = os.getenv("SQL_USER_SOURCE")
    sql_pass_source = os.getenv("SQL_PASSWORD_SOURCE")

    sql_server_dest = os.getenv("SQL_SERVER_DESTINATION")
    sql_database_dest = os.getenv("SQL_DATABASE_DESTINATION")
    sql_user_dest = os.getenv("SQL_USER_DESTINATION")
    sql_pass_dest = os.getenv("SQL_PASSWORD_DESTINATION")

    colunas_sem_id = (
        "nr_titulo, id_cliente, id_pedido, dt_emissao, dt_vencimento, "
        "dt_pagamento, vl_titulo, vl_recebido, ds_status_titulo, "
        "dt_inclusao, dt_atualizacao, nm_sistema_origem, cd_registro_origem"
    )
    
    query_extract = f"SELECT {colunas_sem_id} FROM dbo.titulo_receber"
    
    query_load = f"""
        INSERT INTO dbo.titulo_receber ({colunas_sem_id}) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        logging.info("Conectando ao banco de dados do professor")
        with pymssql.connect(server=sql_server_source, user=sql_user_source, password=sql_pass_source, database=sql_database_source) as conn_source:
            with conn_source.cursor() as cursor_source:
                
                logging.info("Executando extração de dados da tabela dbo.titulo_receber...")
                cursor_source.execute(query_extract)
                rows = cursor_source.fetchall()
                
                if not rows:
                    logging.info("Nenhum dado encontrado na origem. Abortando pipeline.")
                    return
                
                logging.info(f"Sucesso! {len(rows)} registros extraídos para a memória.")

        logging.info("Conectando ao banco de dados de destino")
        with pymssql.connect(server=sql_server_dest, user=sql_user_dest, password=sql_pass_dest, database=sql_database_dest) as conn_dest:
            with conn_dest.cursor() as cursor_dest:
                
                logging.info("Limpando dados antigos")
                cursor_dest.execute("TRUNCATE TABLE dbo.titulo_receber")
                
                logging.info("Inserindo dados")
                cursor_dest.executemany(query_load, rows)
                
                conn_dest.commit()
                
        logging.info("=== PIPELINE EL COM PYMSSQL EXECUTADA COM SUCESSO ===")

    except Exception as e:
        logging.error(f"Falha crítica na execução da pipeline EL (pymssql): {str(e)}")