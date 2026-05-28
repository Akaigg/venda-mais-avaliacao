import logging
import azure.functions as func
import os
import sqlite3

bp = func.Blueprint()

@bp.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def extract_estoque_movimentacao(myTimer: func.TimerRequest) -> None:

    db_file = "/tmp/estoque_local.db"

    logging.info(f"Iniciando conexão com a base de dados SQLite local: {db_file}")
    
    try:
        with sqlite3.connect(db_file) as conn:
            
            cursor = conn.cursor()
                
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estoque_movimentacao (
                    id INTEGER PRIMARY KEY,
                    produto TEXT,
                    quantidade REAL
                )
            """)
            cursor.execute("INSERT INTO estoque_movimentacao (produto, quantidade) VALUES ('Produto Teste', 50.0)")
            conn.commit()
            query = "SELECT * FROM estoque_movimentacao LIMIT 10" 
            cursor.execute(query)
            
            rows = cursor.fetchall()
            
            if not rows:
                logging.info("A tabela estoque_movimentacao está vazia.")
            else:
                logging.info(f"Quantidade de registros encontrados no SQLite: {len(rows)}")
                for row in rows:
                    logging.info(f"Movimentação de Estoque: {list(row)}")
            
            cursor.close()
                        
            logging.info("Consulta via sqlite3 finalizada com sucesso!")
                
    except Exception as e:
        logging.error(f"Erro ao operar na base de dados SQLite: {str(e)}")