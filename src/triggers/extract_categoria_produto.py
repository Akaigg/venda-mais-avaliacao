import logging
import azure.functions as func
import os
import pyodbc

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 0 6 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_categoria_produtos(myTimer: func.TimerRequest) -> None:

    sql_server_source = os.getenv("SQL_SERVER_SOURCE")
    sql_database_source = os.getenv("SQL_DATABASE_SOURCE")
    sql_user_source = os.getenv("SQL_USER_SOURCE")
    sql_password_source = os.getenv("SQL_PASSWORD_SOURCE")

    sql_server_dest = os.getenv("SQL_SERVER_DESTINATION")
    sql_database_dest = os.getenv("SQL_DATABASE_DESTINATION")
    sql_user_dest = os.getenv("SQL_USER_DESTINATION")
    sql_pass_dest = os.getenv("SQL_PASSWORD_DESTINATION")

    logging.info(f"Lendo {sql_database_source} Salvando {sql_database_dest}")

    conn_str_source = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={sql_server_source};"
        f"DATABASE={sql_database_source};"
        f"UID={sql_user_source};"
        f"PWD={sql_password_source};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )

    conn_str_dest = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={sql_server_dest};"
        f"DATABASE={sql_database_dest};"
        f"UID={sql_user_dest};"
        f"PWD={sql_pass_dest};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
   
    try:
        with pyodbc.connect(conn_str_source) as conn_source:
            with conn_source.cursor() as cursor_source:
                query_select = "SELECT * FROM erp.categoria_produto"
                cursor_source.execute(query_select)
                rows = cursor_source.fetchall()

                if not rows:
                    logging.warning("Nenhum registro encontrado (erp.categoria_produto).")
                    return

                columns = [column[0] for column in cursor_source.description]
                logging.info(f"Extração bem-sucedida: {len(rows)} registros encontrados.")

        with pyodbc.connect(conn_str_dest) as conn_dest:
            with conn_dest.cursor() as cursor_dest:
                table_name = "dbo.categoria_produto"

                cursor_dest.execute(f"DELETE FROM {table_name}")
                logging.info(f"Tabela de destino ({table_name}) limpa.")

                cols_str = ",".join(columns)
                placeholders = ",".join(["?" for _ in columns])
                insert_query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders})"

                cursor_dest.execute(f"SET IDENTITY_INSERT {table_name} ON")
                cursor_dest.executemany(insert_query, rows)
                cursor_dest.execute(f"SET IDENTITY_INSERT {table_name} OFF")

                conn_dest.commit()
                logging.info(f"Carga finalizada: {len(rows)} registros inseridos com sucesso no destino.")          

    except pyodbc.Error as e:
        logging.error(f"Erro de SQL: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erro inesperado: {str(e)}")
        raise