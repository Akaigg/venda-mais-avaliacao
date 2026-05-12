import logging
import azure.functions as func

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_cliente(myTimer: func.TimerRequest) -> None:
    logging.info('tabela cliente.')



@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_fornecedor(myTimer: func.TimerRequest) -> None:
    logging.info('tabela fornecedor 3.')


@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_pedido(myTimer: func.TimerRequest) -> None:
    logging.info('tabela pedidos')