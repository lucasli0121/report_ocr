
from datetime import datetime
from typing import Optional
from dataclasses import dataclass
from dao.company_dao import CompanyDao
from dao.invoice_record_dao import InvoiceRecordDao
from dao.tax_approval_dao import TaxApprovalDao
from utils import global_vars as g

@dataclass
class InvoiceRecognizeResult:
    result: int
    msg: str
    data: None|InvoiceRecordDao

def parse_invoice_recognize_result_to_dao(result: list) -> InvoiceRecognizeResult:
    if result is None or len(result) == 0:
        return InvoiceRecognizeResult(result=-1, msg='未识别到发票信息', data=None)
    dao = InvoiceRecordDao()
    dao.invoice_content = result[0].get('发票内容', '')
    dao.invoice_number = result[0].get('发票号码', '')
    invoice_date_str = result[0].get('开票日期', '')
    if invoice_date_str != '':
        try:
            if '年' in invoice_date_str:
                dt = datetime.strptime(invoice_date_str, '%Y年%m月%d日')
            elif '-' in invoice_date_str:
                dt = datetime.strptime(invoice_date_str, '%Y-%m-%d')
            else:
                dt = datetime.strptime(invoice_date_str, '%Y/%m/%d')
            dao.invoice_time = dt.strftime('%Y-%m-%d')
        except ValueError:
            dao.invoice_time = ''
    before_tax_money = result[0].get('含税额', 0.0)
    tax_money = result[0].get('税额', 0.0)
    invoice_money = result[0].get('金额', 0.0)
    tax_rate = result[0].get('税率', 0.0)
    if tax_rate == '1%':
        dao.tax_rate = 0.01
    elif tax_rate == '3%':
        dao.tax_rate = 0.03
    elif tax_rate == '6%':
        dao.tax_rate = 0.06
    elif tax_rate == '9%':
        dao.tax_rate = 0.09
    elif tax_rate == '13%':
        dao.tax_rate = 0.13
    if dao.tax_rate > 0.03:
        dao.invoice_type = 1 # 增值税专用发票
    else:
        dao.invoice_type = 0 # 增值税普通发票
    dao.before_tax_money = before_tax_money
    dao.added_tax = tax_money
    dao.invoice_money = invoice_money
    dao.is_red = 1 if result[0].get('红字发票', False) else 0
    dao.blue_invoice_number = result[0].get('蓝字发票号码', '') if dao.is_red == 1 else ''
    from_company_name = result[0].get('销售方', '')
    to_company_name = result[0].get('购买方', '')
    if from_company_name == '' or to_company_name == '':
        return InvoiceRecognizeResult(result=-1, msg='发票信息不完整，开票方和受票方不能为空', data=None)
    res, from_company_list = g.my_db.query_all_company(from_company_name, '', '', '')
    if not res:
        return InvoiceRecognizeResult(result=-1, msg=f'查询 "{from_company_name}" 失败', data=None)
    if from_company_list is None or len(from_company_list) == 0:
        return InvoiceRecognizeResult(result=-1, msg=f'发票开票方 "{from_company_name}" 不存在，请先添加该公司信息', data=None)
    company_dao: CompanyDao = CompanyDao()
    company_dao.from_db(from_company_list[0])
    dao.from_company_id = company_dao.id
    if to_company_name == '' or to_company_name == '':
        return InvoiceRecognizeResult(result=-1, msg='发票信息不完整，开票方和受票方不能为空', data=None)
    res, to_company_list = g.my_db.query_all_company(to_company_name, '', '', '')
    if not res:
        return InvoiceRecognizeResult(result=-1, msg=f'查询 "{to_company_name}" 失败', data=None)
    if to_company_list is None or len(to_company_list) == 0:
        return InvoiceRecognizeResult(result=-1, msg=f'发票购买方 "{to_company_name}" 不存在，请先添加该公司信息', data=None)
    company_dao.from_db(to_company_list[0])
    dao.to_company_id = company_dao.id
    dao.quantity = result[0].get('数量', 0)
    dao.specifi = result[0].get('规格', '')
    dao.unit_price = result[0].get('单价', 0.0)
    dao.remark = result[0].get('备注', '')
    dao.operator_flag = 1 # 上传发票
    dao.status = 1 # 已开票
    if dao.is_red == 1:
        dao.status = 3 # 已红冲
    return InvoiceRecognizeResult(result=0, msg='成功', data=dao)

def save_invoice_dao(dao: InvoiceRecordDao) -> InvoiceRecognizeResult:
    res, record_list = g.my_db.query_duplicate_invoice_record(dao.from_company_id, dao.to_company_id, dao.invoice_number, dao.invoice_time, dao.invoice_content)
    if res and record_list is not None and len(record_list) > 0:
        return InvoiceRecognizeResult(result=-1, msg=f'发票 "{dao.invoice_number}" 已存在，不能重复上传', data=None)
    res, id = g.my_db.add_invoice_record(dao.to_db())
    if not res:
        return InvoiceRecognizeResult(result=-1, msg='保存发票信息失败', data=None)
    if dao.is_red == 1:
        res, record_list = g.my_db.query_invoice_record_by_number(dao.blue_invoice_number)
        if res and record_list is not None and len(record_list) > 0:
            blue_dao = InvoiceRecordDao()
            blue_dao.from_db(record_list[0])
            blue_dao.status = 2 # 已作废
            if not g.my_db.update_invoice_record(blue_dao.to_db(), {'id': blue_dao.id}):
                return InvoiceRecognizeResult(result=-1, msg='更新蓝字发票状态失败', data=None)
    if id is not None:
        dao.id = id
    return InvoiceRecognizeResult(result=0, msg='保存发票信息成功', data=None)
