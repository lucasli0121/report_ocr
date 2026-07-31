import asyncio
import logging
import logging.config
import os
import signal
import sys
import time
import yaml
from concurrent import futures
from threading import Event
from db.mydb import MyDb
import utils.global_vars as g
from utils.ocr_manager import OcrManager

def init_logger():
    cfg_path = 'cfg/log.yaml'
    if not os.path.exists("log"):
        os.makedirs("log")
    if os.path.exists(cfg_path):
        with open(cfg_path, "r", encoding="utf-8") as f:
            config = yaml.load(f, yaml.FullLoader)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s-%(name)s-%(lineno)s-%(levelname)s-%(message)s",
            filename="log/report_ocr.log",
            filemode="w",
        )
        
# async def serve():
#      server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
#      invoice_rpc_pb2_grpc.add_InvoiceRpcServicer_to_server(InvoiceRecognizeServicer(), server)
#      server.add_insecure_port('[::]:50051')
#      print("Server running...")
#      await server.start()
#      await server.wait_for_termination()

"""
function: signalExit
description: response signal such as SIGTERM, SIGINT
return {*}
"""
exit_event = Event()

def signalExit(a, b):
    try:
        logger.info("exit")
        g.ocr_mgr.stop()
        exit_event.set()
    except Exception:
        pass

if __name__ in {"__main__", "__mp_main__"}:
    init_logger()
    logger = logging.getLogger(__name__)
    g.my_db = MyDb()
    g.ocr_mgr = OcrManager()
    try:
        signal.signal(signal.SIGTERM, signalExit)
        signal.signal(signal.SIGINT, signalExit)
        logger.info("OCR Manager started.")
        g.ocr_mgr.start()
        exit_event.wait()
    except Exception as err:
        logger.error(err)
    except (KeyboardInterrupt, SystemExit):
        pass