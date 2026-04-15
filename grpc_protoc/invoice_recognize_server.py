from configparser import ConfigParser
import logging
import time
import requests
import os
from recognize.certificate_recognize import CertificateRecognizeResult, parse_certificate_result_to_dao, save_certificate_daos
from recognize.invoice_recognize import InvoiceRecognizeResult, parse_invoice_recognize_result_to_dao, save_invoice_dao
from recognize.recognize_tools import recognize_certificate_pdf, recognize_invoice_pdf



class InvoiceRecognizeServicer():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        cp = ConfigParser()
        cp.read("cfg/reportocr.cfg")
        self.download_url = cp.get("download_server", "url")

    def invoice_recognize(self, file_name: str) -> InvoiceRecognizeResult:
        # Simulate invoice recognition logic
        self.logger.info(f"Received invoice recognition file: {file_name}")
        host_url = self.download_url + file_name
        self.logger.info(f"Downloading invoice from URL: {host_url}")
        # Here you would add the logic to download the file and process it
        # For demonstration, we will just simulate a successful response
        http_response = requests.get(host_url)
        if http_response.status_code == 200:
            
            try_num = 0
            return_response: InvoiceRecognizeResult = InvoiceRecognizeResult(result=-1, msg="识别失败", data=None)
            while(try_num < 4):
                result_list = recognize_invoice_pdf(http_response.content, try_num)
                return_response = parse_invoice_recognize_result_to_dao(result_list)
                if return_response.result == 0:
                    break
                try_num += 1
                self.logger.info(f"Invoice recognition attempt {try_num} failed: {return_response.msg}")
                time.sleep(1)  # 等待1秒后重试
            if return_response.result == 0:
                self.logger.info(f"Invoice recognized successfully: {return_response.data}")
                # 保存下载的内容到backup目录
                backup_path = './static/backup/'
                os.makedirs(backup_path, exist_ok=True)
                save_file = os.path.join(backup_path, file_name)
                with open(save_file, 'wb') as f:
                    f.write(http_response.content)
                self.logger.info(f"Downloaded file saved to: {save_file}")
                dao = return_response.data
                if dao is not None:
                    return_response = save_invoice_dao(dao)
                    if return_response.result != 0:
                        self.logger.info(f"Saving invoice failed: {return_response.msg}")
                    else:
                        self.logger.info(f"Invoice saved successfully with ID: {dao.id}")
        else:
            self.logger.info("下载失败，状态码：", http_response.status_code)
            return_response = InvoiceRecognizeResult(result=-1, msg="下载失败，状态码: {http_response.status_code}", data=None)
        return return_response


    def certificate_recognize(self, file_name: str) -> CertificateRecognizeResult:
        # Simulate invoice recognition logic
        self.logger.info(f"Received certificate recognition request for file: {file_name} ")
        host_url = self.download_url + file_name
        self.logger.info(f"Downloading certificate file from URL: {host_url}")
        # Here you would add the logic to download the file and process it
        # For demonstration, we will just simulate a successful response
        http_response = requests.get(host_url)
        return_response: CertificateRecognizeResult = CertificateRecognizeResult(result=-1, msg="识别失败", data=None)
        if http_response.status_code == 200:
            
            try_num = 0
            while(try_num < 4):
                result_list = recognize_certificate_pdf(http_response.content, try_num)
                return_response = parse_certificate_result_to_dao(result_list)
                if return_response.result == 0:
                    break
                try_num += 1
                self.logger.info(f"Certificate recognition attempt {try_num} failed: {return_response.msg}")
                time.sleep(1)  # 等待1秒后重试
            if return_response.result == 0:
                self.logger.info(f"Certificate recognized successfully: {return_response.data}")
                #下载的文件保存到本地static/backup目录下
                # 保存下载的内容到backup目录
                backup_path = './static/backup/'
                os.makedirs(backup_path, exist_ok=True)
                save_file = os.path.join(backup_path, file_name)
                with open(save_file, 'wb') as f:
                    f.write(http_response.content)
                self.logger.info(f"Downloaded file saved to: {save_file}")
                dao_list = return_response.data
                if dao_list is not None:
                    return_response = save_certificate_daos(dao_list)
                    if return_response.result != 0:
                        self.logger.info(f"Saving certificate failed: {return_response.msg}")
                    else:
                        self.logger.info("Certificate saved successfully")
        else:
            self.logger.info("下载失败，状态码：", http_response.status_code)
            return_response = CertificateRecognizeResult(result=-1, msg="下载失败，状态码：{http_response.status_code}", data=None)
        return return_response