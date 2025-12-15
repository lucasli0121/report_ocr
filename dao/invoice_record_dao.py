'''
Author: liguoqiang
Date: 2025-06-01 12:06:35
LastEditors: liguoqiang
LastEditTime: 2025-09-18 16:03:44
Description: 
'''
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any


@dataclass
class InvoiceRecordDao:
    id: str  # 发票记录ID
    invoice_number: str  # 发票号码
    from_company_id: str
    to_company_id: str
    contract_id: str  # 合同ID
    invoice_type: int # 0: 普通发票, 1: 专用发票
    tax_rate: float # 税率
    invoice_content: str # 发票内容
    before_tax_money: float # 税前金额
    added_tax: float # 增值税
    invoice_money: float # 开票金额
    contract_content: str # 合同内容
    status: int # 0: 未开票, 1: 已开票 2: 已作废 3: 已红冲
    create_time: str # 创建时间
    invoice_time: str # 开票时间
    is_red: int # 是否红字发票 0: 否, 1: 是
    blue_invoice_number: str # 蓝字发票号码
    specifi: str # 规格
    quantity: int # 数量
    unit_price: float # 单价
    remark: str # 备注
    operator_flag: int # 操作标志 0: 手工操作, 1: 上传发票
    
    def __init__(self, id:str = '', invoice_number = '', from_company_id: str = "", to_company_id: str = "", contract_id = '', invoice_type: int = 0, tax_rate: float = 0.0,
                 invoice_content: str = "", before_tax_money: float = 0.0, added_tax: float = 0.0,
                 invoice_money: float = 0.0, contract_content: str = "", status: int = 0,
                 create_time: str = "", invoice_time: str="",
                 specifi: str = "", quantity: int = 0, unit_price: float = 0.0, remark: str = "") -> None:
        self.id = id
        self.invoice_number = invoice_number
        self.from_company_id = from_company_id
        self.to_company_id = to_company_id
        self.contract_id = contract_id
        self.invoice_type = invoice_type
        self.tax_rate = tax_rate
        self.invoice_content = invoice_content
        self.before_tax_money = before_tax_money
        self.added_tax = added_tax
        self.invoice_money = invoice_money
        self.contract_content = contract_content
        self.status = status
        self.create_time = create_time if create_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.invoice_time = invoice_time
        self.is_red = 0
        self.blue_invoice_number = ""
        self.specifi = specifi
        self.quantity = quantity
        self.unit_price = unit_price
        self.remark = remark

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.invoice_number = str(data.get('invoice_number', ''))
        self.from_company_id = str(data.get('from_company_id', ''))
        self.to_company_id = str(data.get('to_company_id', ''))
        self.contract_id = str(data.get('contract_id', ''))
        self.invoice_type = int(data.get('invoice_type', 0))
        self.tax_rate = float(data.get('tax_rate', 0.0))
        self.invoice_content = str(data.get('invoice_content', ''))
        self.before_tax_money = float(data.get('before_tax_money', 0.0))
        self.added_tax = float(data.get('added_tax', 0.0))
        self.invoice_money = float(data.get('invoice_money', 0.0))
        self.contract_content = str(data.get('contract_content', ''))
        self.status = int(data.get('status', 0))
        self.create_time = str(data.get('create_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.invoice_time = str(data.get('invoice_time', ''))
        self.specifi = str(data.get('specifi', ''))
        self.quantity = int(data.get('quantity', 0))
        self.unit_price = float(data.get('unit_price', 0.0))
        self.remark = str(data.get('remark', ''))
        self.operator_flag = int(data.get('operator_flag', 0))
        self.is_red = int(data.get('is_red', 0))
        self.blue_invoice_number = str(data.get('blue_invoice_number', ''))

    def to_db(self) -> dict[str, Any]:
        return self.__dict__