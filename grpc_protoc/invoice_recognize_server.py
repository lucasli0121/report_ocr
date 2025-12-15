from configparser import ConfigParser
import logging
import grpc
import time
from concurrent import futures

import requests
from dao.invoice_record_dao import InvoiceRecordDao
from grpc_protoc import invoice_rpc_pb2
from grpc_protoc import invoice_rpc_pb2_grpc
from recognize.certificate_recognize import parse_certificate_result_to_dao, save_certificate_daos
from recognize.invoice_recognize import InvoiceRecognizeResult, parse_invoice_recognize_result_to_dao, save_invoice_dao
from recognize.recognize_tools import recognize_certificate_pdf, recognize_invoice_pdf
from utils import global_vars as g



class InvoiceRecognizeServicer(invoice_rpc_pb2_grpc.InvoiceRpcServicer):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        cp = ConfigParser()
        cp.read("cfg/reportocr.cfg")
        self.download_url = cp.get("download_server", "url")

    async def invoice_recognize(self, request, context):
        # Simulate invoice recognition logic
        file_name = request.file_name
        flag = request.flag
        self.logger.info(f"Received invoice recognition request for file: {file_name} with flag: {flag}")
        host_url = self.download_url + file_name
        self.logger.info(f"Downloading invoice from URL: {host_url}")
        # Here you would add the logic to download the file and process it
        # For demonstration, we will just simulate a successful response
        response = requests.get(host_url)
        if response.status_code == 200:
            result_list = recognize_invoice_pdf(response.content)
            parse_response = parse_invoice_recognize_result_to_dao(result_list)
            if parse_response.result != 0:
                self.logger.info(f"Invoice recognition failed: {parse_response.msg}")
                yield invoice_rpc_pb2.InvoiceRecognizeResp(
                    result=parse_response.result,
                    msg=parse_response.msg,
                    id="",
                )
            else:
                self.logger.info(f"Invoice recognized successfully: {parse_response.data}")
                dao = parse_response.data
                if dao is not None:
                    save_response = save_invoice_dao(dao)
                    if save_response.result != 0:
                        self.logger.info(f"Saving invoice failed: {save_response.msg}")
                        yield invoice_rpc_pb2.InvoiceRecognizeResp(
                            result=save_response.result,
                            msg=save_response.msg,
                            id="",
                        )
                    else:
                        self.logger.info(f"Invoice saved successfully with ID: {dao.id}")
                        yield invoice_rpc_pb2.InvoiceRecognizeResp(
                            result=0,
                            msg="发票识别并保存成功",
                            id=str(dao.id),
                        )
        else:
            self.logger.info("下载失败，状态码：", response.status_code)
        response = invoice_rpc_pb2.InvoiceRecognizeResp(
            result=-1,
            msg="下载失败",
            id="",
        )
        yield response


    async def certificate_recognize(self, request, context):
        # Simulate invoice recognition logic
        file_name = request.file_name
        flag = request.flag
        self.logger.info(f"Received certificate recognition request for file: {file_name} with flag: {flag}")
        host_url = self.download_url + file_name
        self.logger.info(f"Downloading certificate file from URL: {host_url}")
        # Here you would add the logic to download the file and process it
        # For demonstration, we will just simulate a successful response
        response = requests.get(host_url)
        if response.status_code == 200:
            result_list = recognize_certificate_pdf(response.content)
            parse_response = parse_certificate_result_to_dao(result_list)
            if parse_response.result != 0:
                self.logger.info(f"Certificate recognition failed: {parse_response.msg}")
                yield invoice_rpc_pb2.InvoiceRecognizeResp(
                    result=parse_response.result,
                    msg=parse_response.msg,
                    id="",
                )
            else:
                self.logger.info(f"Certificate recognized successfully: {parse_response.data}")
                dao_list = parse_response.data
                if dao_list is not None:
                    save_response = save_certificate_daos(dao_list)
                    if save_response.result != 0:
                        self.logger.info(f"Saving certificate failed: {save_response.msg}")
                        yield invoice_rpc_pb2.InvoiceRecognizeResp(
                            result=save_response.result,
                            msg=save_response.msg,
                            id="",
                        )
                    else:
                        self.logger.info("Certificate saved successfully")
                        yield invoice_rpc_pb2.InvoiceRecognizeResp(
                            result=0,
                            msg="完税证明识别并保存成功",
                            id="",
                        )
        else:
            self.logger.info("下载失败，状态码：", response.status_code)
        response = invoice_rpc_pb2.InvoiceRecognizeResp(
            result=-1,
            msg="下载失败",
            id="",
        )
        yield response