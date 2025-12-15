import asyncio
import logging
import os
import grpc
from concurrent import futures
import logging.config
import yaml
from grpc_protoc.invoice_recognize_server import InvoiceRecognizeServicer
from grpc_protoc import invoice_rpc_pb2_grpc

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
            filename="log/beautify_report.log",
            filemode="w",
        )
        
async def serve():
     server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
     invoice_rpc_pb2_grpc.add_InvoiceRpcServicer_to_server(InvoiceRecognizeServicer(), server)
     server.add_insecure_port('[::]:50051')
     print("Server running...")
     await server.start()
     await server.wait_for_termination()

if __name__ in {"__main__", "__mp_main__"}:
    init_logger()
    logger = logging.getLogger(__name__)
    asyncio.run(serve())