from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ServiceRecordDao:
    id: str  # 发票记录ID
    from_company_id: str
    to_company_id: str
    contract_money: float # 合同金额
    contract_name: str # 合同名称
    contract_content: str # 合同内容
    is_contract: int # 是否有合同
    invoice_money: float # 已开票金额
    payment_money: float # 已付款金额
    latest_payment_time: str # 最近付款时间
    latest_invoice_time: str # 最近开票时间
    status: int # 状态 0: 未完成, 1: 无合同 2: 待付款 3:待开票 4:完成
    create_time: str
    
    def __init__(self, id: str = '', from_company_id: str = "", to_company_id: str = "", contract_money: float = 0.0,
                 contract_name: str = "", contract_content: str = '', is_contract: int = 0, invoice_money: float = 0.0,
                 payment_money: float = 0.0, latest_payment_time: str = "", latest_invoice_time: str = "", status: int = 0, create_time: str = "") -> None:
        self.id = id
        self.from_company_id = from_company_id
        self.to_company_id = to_company_id
        self.contract_money = contract_money
        self.contract_name = contract_name
        self.contract_content = contract_content
        self.is_contract = is_contract
        self.invoice_money = invoice_money
        self.payment_money = payment_money
        self.latest_payment_time = latest_payment_time if latest_payment_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.latest_invoice_time = latest_invoice_time if latest_invoice_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status = status
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.from_company_id = str(data.get('from_company_id', ''))
        self.to_company_id = str(data.get('to_company_id', ''))
        contract_money_str = str(data.get('contract_money', 0.0)).replace(',', '').strip()
        self.contract_money = float(contract_money_str)
        self.contract_name = str(data.get('contract_name', ''))
        self.contract_content = str(data.get('contract_content', ''))
        self.is_contract = int(data.get('is_contract', 0))
        invoice_money = str(data.get('invoice_money', 0.0)).replace(',', '').strip()
        self.invoice_money = float(invoice_money)
        payment_money = str(data.get('payment_money', 0.0)).replace(',', '').strip()
        self.payment_money = float(payment_money)
        self.latest_payment_time = str(data.get('latest_payment_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.latest_invoice_time = str(data.get('latest_invoice_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.status = int(data.get('status', 0))
        self.create_time = str(data.get('create_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__