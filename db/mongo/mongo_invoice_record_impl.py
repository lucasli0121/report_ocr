'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 19:35:46
Description: 
'''
# coding="utf8"

from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.invoice_record_dao import InvoiceRecordDao
from db.mongo.mongo_impl import MongoImpl

class MongoInvoiceRecordImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 开票记录表名
    def invoice_record_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['invoice_record_tbl']
    
    
    """
    添加开票记录
    :param data: 开票记录信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    更新开票记录信息到数据库
    :param data: 开票记录字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询开票记录信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_number: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if from_company_id or len(from_company_id) > 0:
            query['from_company_id'] = {'$eq': from_company_id}
        if to_company_id or len(to_company_id) > 0:
            query['to_company_id'] = {'$eq': to_company_id}
        if invoice_content or len(invoice_content) > 0:
            query['invoice_content'] = {'$regex': invoice_content, '$options': 'i'}
        if invoice_number or len(invoice_number) > 0:
            query['invoice_number'] = {'$eq': invoice_number}
        if status >= 0:
            query['status'] = {'$eq': status}
        if begin_time or len(begin_time) > 0:
            query['create_time'] = {'$gte': begin_time}
        if end_time or len(end_time) > 0:
            if 'create_time' in query:
                query['create_time']['$lte'] = end_time
            else:
                query['create_time'] = {'$lte': end_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    """
    查询开票记录信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_by_time(self, from_company_id: str, to_company_id: str, invoice_content: str, invoice_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if from_company_id or len(from_company_id) > 0:
            query['from_company_id'] = {'$eq': from_company_id}
        if to_company_id or len(to_company_id) > 0:
            query['to_company_id'] = {'$eq': to_company_id}
        # if invoice_content or len(invoice_content) > 0:
        #     query['invoice_content'] = {'$regex': invoice_content, '$options': 'i'}
        if invoice_time or len(invoice_time) > 0:
            query['invoice_time'] = {'$eq': invoice_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    def query_duplicate_invoice(self, from_company_id: str, to_company_id: str, invoice_number: str, invoice_time: str, invoice_content: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if invoice_number or len(invoice_number) > 0:
            query['invoice_number'] = {'$eq': invoice_number}
        else:
            if from_company_id or len(from_company_id) > 0:
                query['from_company_id'] = {'$eq': from_company_id}
            if to_company_id or len(to_company_id) > 0:
                query['to_company_id'] = {'$eq': to_company_id}
            if invoice_time or len(invoice_time) > 0:
                query['invoice_time'] = {'$eq': invoice_time}
            if invoice_content or len(invoice_content) > 0:
                query['invoice_content'] = {'$regex': invoice_content, '$options': 'i'}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    
    def query_by_number(self, invoice_number: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if invoice_number or len(invoice_number) > 0:
            query['invoice_number'] = {'$eq': invoice_number}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'invoice_time': -1})
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, InvoiceRecordDao|None]:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        if id is None or len(id) == 0:
            return False, None
        query = {'_id': ObjectId(id)}
        result, value = self.mongo_impl.query_by_condition(tbl_name, query, None)
        if not result or value is None:
            self.logger.error("No invoice record found with the given ID.")
            return False, None
        dao = InvoiceRecordDao()
        dao.from_db(value[0])
        return True, dao
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.invoice_record_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
