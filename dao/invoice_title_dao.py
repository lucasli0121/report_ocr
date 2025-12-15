from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any


@dataclass
class InvoiceTitleDao:
    id: str  # 发票抬头ID
    company_id: str
    bank_name: str # 开户行
    bank_account: str # 银行账号
    contact_phone: str # 联系电话
    create_time: str
    
    def __init__(self, id='', company_id='', bank_name='', bank_account='', contact_phone='', create_time=''):
        self.id = str(id)
        self.company_id = str(company_id)
        self.bank_name = bank_name
        self.bank_account = bank_account
        self.contact_phone = contact_phone
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = str(data.get('company_id', ''))
        self.bank_name = data.get('bank_name', '')
        self.bank_account = data.get('bank_account', '')
        self.contact_phone = data.get('contact_phone', '')
        self.create_time = str(data.get('create_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__