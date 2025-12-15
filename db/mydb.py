'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 15:52:07
Description: mydb 类，数据库代理类，根据配置文件选择数据库实现类
    包括mysql, mongo
'''
# coding="utf8"

from datetime import datetime
from typing import Any
from configparser import ConfigParser, NoSectionError
import logging
from db.mongo.mongo_impl import MongoImpl
from db.mongo.mongo_invoice_title_impl import MongoInvoiceTitleImpl
from db.mysql.mysql_db import MySqlImpl
from db.mongo.mongo_company_impl import MongoCompanyImpl
from db.mongo.mongo_invoice_record_impl import MongoInvoiceRecordImpl
from db.mongo.mongo_payment_record_impl import MongoPaymentRecordImpl
from db.mongo.mongo_service_record_impl import MongoServiceRecordImpl
from db.mongo.mongo_tax_approval_impl import MongoTaxApprovalImpl
from db.mysql.mysql_company_impl import MySqlCompanyImpl
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import CompanyBankAccountDao
from dao.tax_approval_dao import TaxApprovalDao

class MyDb:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        cp = ConfigParser()
        cp.read("cfg/reportocr.cfg")
        self.mongo = None
        self.mysql = None
        try:
            self.enable_mysql = cp.get("default", "mysql_enable")
            self.enable_mongo = cp.get("default", "mongo_enable")
            if self.enable_mysql == "true":
                self.mysql = MySqlImpl()
            if self.enable_mongo == "true":
                self.mongo = MongoImpl()
        except NoSectionError as err:
            self.logger.error("not find section:", err.message)
        
    def __del__(self):
        if self.mongo is not None:
            del self.mongo
        if self.mysql is not None:
            del self.mysql
            
    '''
    function: add_company
    description: 添加公司信息
    param {*} self
    param {*} d
    return {*}
    '''    
    def add_company(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).add_company(d)
        self.logger.error("No database implementation available for adding company.")
        return False, None
    
    def query_same_company(self, name: str, brief_name: str) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_same_company(name, brief_name)
        self.logger.error("No database implementation available for querying same company.")
        return False, None
    '''
    function: update_company
    description: 更新公司信息
    param {*} self
    param {*} d
    return {*}
    '''    
    def update_company(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            mysql_condition = ''
            if id in condition:
                # 如果condition中有id字段，则使用id作为更新条件
                # condition = f"id = {condition['id']}"
                mysql_condition = f"id = {condition['id']}"
            return MySqlCompanyImpl(self.mysql).update_company(d, mysql_condition)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).update_company(d, condition)
        self.logger.error("No database implementation available for updating company.")
        return False
    
    def query_all_company(self, name: str, address: str, contacts: str, company_type: str) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_all_company(name, address, contacts)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_all_company(name, address, contacts, company_type)
        self.logger.error("No database implementation available for querying company.")
        return False, None
    def query_inner_company(self, name: str, address: str, contacts: str, company_type: str) -> tuple[bool, None|list[Any]]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_all_company(name, address, contacts)
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_inner_company(name, address, contacts, company_type)
        self.logger.error("No database implementation available for querying company.")
        return False, None
    
    def query_company_by_id(self, id: str) -> tuple[bool, CompanyDao|None]:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).query_company_by_id(int(id))
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_by_id(id)
        self.logger.error("No database implementation available for querying company by id.")
        return False, None
    
    def query_company_by_brief_name(self, brief_name: str) -> tuple[bool, CompanyDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_by_brief_name(brief_name)
        self.logger.error("No database implementation available for querying company by brief name.")
        return False, None
    
    def delete_company(self, id: str) -> bool:
        if self.mysql is not None:
            return MySqlCompanyImpl(self.mysql).delete_company(int(id))
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).delete_company(id)
        self.logger.error("No database implementation available for deleting company.")
        return False
    
    def add_company_bank_account(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).add_company_bank_account(d)
        self.logger.error("No database implementation available for adding company bank account.")
        return False, None
    def update_company_bank_account(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).update_company_bank_account(d, condition)
        self.logger.error("No database implementation available for updating company bank account.")
        return False
    def query_all_company_bank_account(self, company_id: str) -> tuple[bool, None|list[CompanyBankAccountDao]]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_all_company_bank_account(company_id)
        self.logger.error("No database implementation available for querying company bank account.")
        return False, None
    def query_company_bank_account_by_id(self, id: str) -> tuple[bool, CompanyBankAccountDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).query_company_bank_account_by_id(id)
        self.logger.error("No database implementation available for querying company bank account by id.")
        return False, None
    
    def delete_company_bank_account(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoCompanyImpl(self.mongo).delete_company_bank_account(id)
        self.logger.error("No database implementation available for deleting company bank account.")
        return False
    def add_invoice_title(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding invoice title.")
        return False, None
    def update_invoice_title(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating invoice title.")
        return False
    def query_invoice_title_all(self, company_id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).query_all(company_id)
        self.logger.error("No database implementation available for querying invoice title.")
        return False, None
    def query_invoice_title_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying invoice title by id.")
        return False, None
    def delete_invoice_title(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceTitleImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting invoice title.")
        return False
    def add_invoice_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding invoice record.")
        return False, None
    def update_invoice_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating invoice record.")
        return False
    def query_invoice_record_by_time(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_time(from_company_id, to_company_id, invoice_content, invoice_time)
        self.logger.error("No database implementation available for querying invoice record.")
        return False, None
    
    def query_all_invoice_record(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_number: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_all(from_company_id, to_company_id, invoice_content, invoice_number, status, begin_time, end_time)
        self.logger.error("No database implementation available for querying invoice record.")
        return False, None
    def query_invoice_record_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying invoice record by id.")
        return False, None
    
    def query_duplicate_invoice_record(self, from_company_id: str, to_company_id: str, invoice_number: str, invoice_time: str, invoice_content: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_duplicate_invoice(from_company_id, to_company_id, invoice_number, invoice_time, invoice_content)
        self.logger.error("No database implementation available for querying duplicate invoice record.")
        return False, None
    
    def query_invoice_record_by_number(self, invoice_number: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).query_by_number(invoice_number)
        self.logger.error("No database implementation available for querying invoice record by number.")
        return False, None
    def delete_invoice_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoInvoiceRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting invoice record.")
        return False
    
    def add_payment_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding payment record.")
        return False, None
    def update_payment_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating payment record.")
        return False
    def query_all_payment_record(self, from_company_id: str, to_company_id: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).query_all(from_company_id, to_company_id, status, begin_time, end_time)
        self.logger.error("No database implementation available for querying payment record.")
        return False, None
    def query_payment_record_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying payment record by id.")
        return False, None
    def delete_payment_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoPaymentRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting payment record.")
        return False
    def add_service_record(self, d: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).add(d)
        self.logger.error("No database implementation available for adding service record.")
        return False, None
    def update_service_record(self, d: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).update(d, condition)
        self.logger.error("No database implementation available for updating service record.")
        return False
    def query_all_service_record(self, from_company_id: str, to_company_id: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).query_all(from_company_id, to_company_id, status, begin_time, end_time)
        self.logger.error("No database implementation available for querying service record.")
        return False, None
    def query_service_record_by_id(self, id: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying service record by id.")
        return False, None
    def delete_service_record(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoServiceRecordImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting service record.")
        return False
    
    ############################################################################################################
    # 完税证明相关接口 
    ############################################################################################################
    """
    function: add_tax_approval
    description: 添加完税证明信息到数据库
    :param {*} self
    :param data: 完税证明信息字典
    :return: 成功返回True，否则返回False    
    """    
    def add_tax_approval(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).add(data)
        self.logger.error("No database implementation available for adding tax approval.")
        return False, None 
    """ 
    更新完税证明信息到数据库
    :param {*} self
    :param data: 完税证明字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_tax_approval(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).update(data, condition)
        self.logger.error("No database implementation available for updating tax approval.")
        return False
    """
    查询完税证明信息
    :param {*} self
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_tax_approval(self, company_id: str, approval_no: str, ori_voucher_number: str, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_all(company_id, approval_no, ori_voucher_number, begin_time, end_time)
        self.logger.error("No database implementation available for querying tax approval.")
        return False, None
    """
    function:
    description: 从服务器查询信息
    :param {*} self
    :param id: 完税证明ID
    :return: {*}
    """
    def query_tax_approval_by_id(self, id: str) -> tuple[bool, TaxApprovalDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_by_id(id)
        self.logger.error("No database implementation available for querying tax approval by id.")
        return False, None
    """
    function:
    description: 从服务器查询信息
    :param {*} self
    :param id: 完税证明No
    :return: {*}
    """
    def query_tax_approval_by_no(self, no: str) -> tuple[bool, TaxApprovalDao|None]:
        if self.mysql is not None:
            return False, None
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).query_by_approval_no(no)
        self.logger.error("No database implementation available for querying tax approval by id.")
        return False, None
    """
    function:
    description: 删除完税证明信息
    :param {*} self
    :param id: 完税证明ID
    :return: {*}
    """
    def delete_tax_approval(self, id: str) -> bool:
        if self.mysql is not None:
            return False
        else:
            if self.mongo is not None:
                return MongoTaxApprovalImpl(self.mongo).delete(id)
        self.logger.error("No database implementation available for deleting tax approval.")
        return False