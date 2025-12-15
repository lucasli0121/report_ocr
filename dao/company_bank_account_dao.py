from dataclasses import dataclass
import logging
from typing import Any

logger = logging.getLogger(__name__)

@dataclass
class CompanyBankAccountDao:
    id: str
    company_id: str
    bank_account: str
    bank_name: str
    account_type: int # 0: 基本户, 1: 一般户, 2: 
    bank_address: str
    
    def __init__(self, id: str = "", company_id: str = "", bank_account: str = "", bank_name: str = "", account_type: int = 0, bank_address: str = "") -> None:
        self.id = id
        self.company_id = company_id
        self.bank_account = bank_account
        self.bank_name = bank_name
        self.account_type = account_type
        self.bank_address = bank_address

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.company_id = str(data.get('company_id', ''))
        self.bank_account = str(data.get('bank_account', ''))
        self.bank_name = str(data.get('bank_name', ''))
        self.account_type = int(data.get('account_type', 0))
        self.bank_address = str(data.get('bank_address', ''))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__
    

