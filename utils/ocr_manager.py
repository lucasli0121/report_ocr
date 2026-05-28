
from dataclasses import asdict, dataclass, is_dataclass
import json
import os
from configparser import ConfigParser, NoOptionError, NoSectionError
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from grpc_protoc.invoice_recognize_server import InvoiceRecognizeServicer
from recognize.recognize_result import CertificateRecognizeResult, InvoiceRecognizeResult
from utils import global_vars as g
from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType


@dataclass
class EventObj:
    id: str
    type: int
    result: int
    msg: str


class OcrManager:
    scheduler: BackgroundScheduler
    recognize_servere: InvoiceRecognizeServicer = InvoiceRecognizeServicer()
    _is_running: bool = False
    
    def __init__(self) -> None:
        self.scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
        self._is_running = False

    def start(self):
        if self._is_running:
            print("OcrManager scheduler is already running, skipping start()")
            return
        self._is_running = True
        self.scheduler.add_job(self.process_ocr_files, 'interval', max_instances=1, seconds=30)
        self.scheduler.start()

    def stop(self):
        self._is_running = False
        try:
            self.scheduler.shutdown()
        except Exception as e:
            print(f"Error occurred while stopping scheduler: {e}")

    def _get_ocr_result_api_url(self) -> str | None:
        cfg_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cfg', 'reportocr.cfg')
        config = ConfigParser()
        config.read(cfg_path, encoding='utf-8')
        try:
            return config.get('ocr_result_api', 'url')
        except (NoSectionError, NoOptionError):
            return None

    def _to_json_payload(self, event_obj: Any) -> dict[str, Any]:
        if isinstance(event_obj, dict):
            return event_obj
        if is_dataclass(event_obj):
            return asdict(event_obj)
        if hasattr(event_obj, '__dict__'):
            return dict(vars(event_obj))
        return {'event': str(event_obj)}

    def post_ocr_result(self, event_obj: dict[str, Any]):
        api_url = self._get_ocr_result_api_url()
        if api_url:
            payload = self._to_json_payload(event_obj)
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            request_obj = Request(api_url, data=body, headers=headers, method='POST')
            try:
                with urlopen(request_obj, timeout=10) as response:
                    response.read()
            except HTTPError as err:
                print(f'post_ocr_result HTTP error {err.code}: {err.reason}')
            except URLError as err:
                print(f'post_ocr_result URL error: {err.reason}')
            except Exception as err:
                print(f'post_ocr_result unexpected error: {err}')
        else:
            print('post_ocr_result skipped: no ocr_result_api.url configured')


    def process_ocr_files(self) -> None:
        res, list_values = g.my_db.query_recognize_waiting_list_by_type(RecognizeType.AllType.value)
        if res and list_values is not None:
            for item in list_values:
                dao = RecognizeInfoDao()
                dao.from_db(item)
                dao.result = RecognizeResult.InProgress.value
                dao.msg = '识别中'
                g.my_db.update_recognize_info(dao.to_db(), {'id': dao.id})
                # 发送一个post事件，让服务端知道正在处理这个文件了
                self.post_ocr_result({ "id": dao.id, "type": dao.type, "result": dao.result, "msg": dao.msg })
                response: InvoiceRecognizeResult|CertificateRecognizeResult|None = None
                if dao.type == RecognizeType.InvoiceType.value:
                    response = self.recognize_servere.invoice_recognize(dao.file_name)
                elif dao.type == RecognizeType.TaxProofType.value:
                    response = self.recognize_servere.certificate_recognize(dao.file_name)
                if response is not None:
                    if response.result == 0:
                        dao.result = RecognizeResult.Success.value
                        dao.msg = response.msg
                    else:
                        dao.result = RecognizeResult.Failed.value
                        dao.msg = response.msg
                    g.my_db.update_recognize_info(dao.to_db(), {'id': dao.id})
                    self.post_ocr_result({ "id": dao.id, "type": dao.type, "result": dao.result, "msg": dao.msg })
                else:
                    self.post_ocr_result({ "id": dao.id, "type": dao.type, "result": RecognizeResult.Failed.value, "msg": "识别失败" })


    