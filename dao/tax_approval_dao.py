'''
Author: liguoqiang
Date: 2025-06-01 12:06:35
LastEditors: liguoqiang
LastEditTime: 2025-09-18 16:03:44
Description: 完税证明的数据访问对象
'''
from dataclasses import dataclass
from datetime import datetime
import json
from typing import Any


@dataclass
class TaxApprovalDao:
    id: str  # ID
    approval_no: str  # 完税号码
    company_id: str
    tax_authority: str # 税务机关
    ori_voucher_number: str # 原始凭证号码
    tax_type: str # 税种
    item_name: str # 品目名称
    tax_period: str # 税款所属日期
    entry_date: str # 入库日期
    paid_in_money: float # 实缴金额
    total_money: float # 总金额
    create_time: str  # 创建时间
    remark: str # 备注
    
    def __init__(self, id:str = '', approval_no = '', company_id: str = "", tax_authority: str = "", ori_voucher_number = '', tax_type: str = "", item_name: str = "",
                 tax_period: str = "", entry_date: str = "", paid_in_money: float = 0.0,
                 total_money: float = 0.0, create_time: str = "", remark: str = "") -> None:
        self.id = id
        self.approval_no = approval_no
        self.company_id = company_id
        self.tax_authority = tax_authority
        self.ori_voucher_number = ori_voucher_number
        self.tax_type = tax_type
        self.item_name = item_name
        self.tax_period = tax_period
        self.entry_date = entry_date
        self.paid_in_money = paid_in_money
        self.total_money = total_money
        self.create_time = create_time
        self.remark = remark

    def from_db(self, data: dict[str, Any]) -> None:
        self.id = str(data.get('_id', ''))
        self.approval_no = data.get('approval_no', '')
        self.company_id = data.get('company_id', '')
        self.tax_authority = data.get('tax_authority', '')
        self.ori_voucher_number = data.get('ori_voucher_number', '')
        self.tax_type = data.get('tax_type', '')
        self.item_name = data.get('item_name', '')
        self.tax_period = data.get('tax_period', '')
        self.entry_date = data.get('entry_date', '')
        self.paid_in_money = data.get('paid_in_money', 0.0)
        self.total_money = data.get('total_money', 0.0)
        self.create_time = data.get('create_time', '')
        self.remark = data.get('remark', '')

    def to_db(self) -> dict[str, Any]:
        return self.__dict__