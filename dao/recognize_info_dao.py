from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging
from typing import Any

logger = logging.getLogger(__name__)

class RecognizeType(Enum):
    AllType = -1  # 所有类型
    InvoiceType = 1  # 发票识别文件
    TaxProofType = 2 # 完税证明识别文件

class RecognizeResult(Enum):
    Failed = -1  # 识别失败
    InProgress = 0  # 识别中
    Success = 1  # 识别成功
    Waiting = 2  # 待识别

@dataclass
class RecognizeInfoDao:
    id: str
    file_name: str
    type: int # 1: 发票识别文件 2: 完税证明识别文件
    result: int # -1: 识别失败 0: 识别中 1: 识别成功 2: 待识别
    retry_count: int # 重试次数
    msg: str
    create_time: str

    def __init__(self, id="", file_name="", type=1, result=0, retry_count=0, msg="", create_time=""):
        self.id = str(id)
        self.file_name = file_name
        self.type = RecognizeType(type).value
        self.result = RecognizeResult(result).value
        self.retry_count = retry_count
        self.msg = msg
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def from_db(self, data: dict[str, Any]) -> None:
        if '_id' in data:
            self.id = str(data['_id'])
        else:
            self.id = str(data.get('id', 0))
        self.file_name = data.get('file_name', "")
        self.type = data.get('type', RecognizeType.InvoiceType.value)
        self.result = data.get('result', RecognizeResult.InProgress.value)
        self.retry_count = data.get('retry_count', 0)
        self.msg = data.get('msg', "")
        self.create_time = data.get('create_time', "")
        

    def to_db(self) -> dict[str, Any]:
        return self.__dict__
    

