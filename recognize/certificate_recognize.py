
from datetime import datetime
import re
from typing import Optional
from dataclasses import dataclass
from dao.company_dao import CompanyDao
from dao.tax_approval_dao import TaxApprovalDao
from utils import global_vars as g

@dataclass
class CertificateRecognizeResult:
    result: int
    msg: str
    data: None|list[TaxApprovalDao]

def parse_certificate_result_to_dao(results: list) -> CertificateRecognizeResult:
    if results is None or len(results) == 0:
        return CertificateRecognizeResult(result=-1, msg='未识别到任何信息', data=None)
    result_data = results[0]
    ori_number_list = result_data.get('原凭证号', [])
    tax_type_list = result_data.get('税种', [])
    item_name_list = result_data.get('品目名称', [])
    tax_period_list = result_data.get('税款所属日期', [])
    entry_date_list = result_data.get('入库日期', [])
    paid_in_money_list = result_data.get('实缴金额', [])
    company_name = result_data.get('名称', '')
    result, company_list = g.my_db.query_all_company(company_name, '', '', '')
    if result is False or company_list is None or len(company_list) == 0:
        return CertificateRecognizeResult(result=-1, msg=f'上传文件中的公司名称 {company_name} 未在系统中找到，请先添加公司信息', data=None)
    if ori_number_list is None or len(ori_number_list) == 0:
        return CertificateRecognizeResult(result=-1, msg='上传文件中未识别到原凭证号，上传失败', data=None)
    company_dao = CompanyDao()
    company_dao.from_db(company_list[0])
    dao_list: list[TaxApprovalDao] = []
    for i in range(len(ori_number_list)):
        dao = TaxApprovalDao()
        dao.company_id = company_dao.id
        dao.approval_no = result_data.get('No', '')
        text = result_data.get('日期', '')
        pattern = r"^(\d{4})年(\d{1,2})月(\d{1,2})日$"
        if re.match(pattern, text):
            dao.create_time = re.sub(pattern, r"\1-\2-\3", text)
        else:
            dao.create_time = text  # 不匹配则保持原样
        dao.tax_authority = result_data.get('税务机关', '')
        dao.ori_voucher_number = ori_number_list[i]
        dao.tax_type = tax_type_list[i] if i < len(tax_type_list) else ''
        dao.tax_period = tax_period_list[i] if i < len(tax_period_list) else ''
        dao.item_name = item_name_list[i] if i < len(item_name_list) else ''
        dao.entry_date = entry_date_list[i] if i < len(entry_date_list) else ''
        dao.paid_in_money = float(paid_in_money_list[i]) if i < len(paid_in_money_list) else 0.0
        dao.total_money = float(result_data.get('总金额', 0.0))
        dao.remark = result_data.get('备注', '')
        dao_list.append(dao)
    return CertificateRecognizeResult(result=0, msg='识别成功', data=dao_list)

def save_certificate_daos(dao_list: list[TaxApprovalDao]) -> CertificateRecognizeResult:
    for dao in dao_list:
        res, msg = g.my_db.add_tax_approval(dao.to_db())
        if not res:
            return CertificateRecognizeResult(result=-1, msg=f'保存税务批准文件失败: {msg}', data=None)
    return CertificateRecognizeResult(result=0, msg='保存税务批准文件成功', data=dao_list)