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
from dao.tax_approval_dao import TaxApprovalDao
from db.mongo.mongo_impl import MongoImpl

class MongoTaxApprovalImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 完税证明表
    def tax_approval_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['tax_approval_tbl']
    
    
    """
    添加完税证明
    :param data: 完税证明信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.tax_approval_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    更新完税证明信息到数据库
    :param data: 完税证明字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.tax_approval_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询完税证明信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, company_id: str, approval_no: str, ori_voucher_number: str, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.tax_approval_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query = {}
        if company_id or len(company_id) > 0:
            query['company_id'] = {'$eq': company_id}
        if approval_no or len(approval_no) > 0:
            query['approval_no'] = {'$eq': approval_no}
        if ori_voucher_number or len(ori_voucher_number) > 0:
            query['ori_voucher_number'] = {'$eq': ori_voucher_number}
        if begin_time or len(begin_time) > 0:
            query['create_time'] = {'$gte': begin_time}
        if end_time or len(end_time) > 0:
            if 'create_time' in query:
                query['create_time']['$lte'] = end_time
            else:
                query['create_time'] = {'$lte': end_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'create_time': -1})
    
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, TaxApprovalDao|None]:
        tbl_name = self.tax_approval_tbl()
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
        dao = TaxApprovalDao()
        dao.from_db(value[0])
        return True, dao
    """
    function:
    description: 从服务器查询信息,根据完税号码查询
    param {*} course
    return {*}
    """
    def query_by_approval_no(self, no: str) -> tuple[bool, TaxApprovalDao|None]:
        tbl_name = self.tax_approval_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        if no is None or len(no) == 0:
            return False, None
        query = {'approval_no': {'$eq': no}}
        result, value = self.mongo_impl.query_by_condition(tbl_name, query, None)
        if not result or value is None:
            self.logger.error("No invoice record found with the given ID.")
            return False, None
        dao = TaxApprovalDao()
        dao.from_db(value[0])
        return True, dao
    
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.tax_approval_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
