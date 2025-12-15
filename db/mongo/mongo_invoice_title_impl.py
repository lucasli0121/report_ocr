'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2024-06-06 21:00:51
Description: 
'''
# coding="utf8"

from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.invoice_title_dao import InvoiceTitleDao
from db.mongo.mongo_impl import MongoImpl

class MongoInvoiceTitleImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 发票抬头表名
    def invoice_title_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['invoice_title_tbl']
    
    
    """
    添加发票抬头
    :param data: 发票抬头信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.invoice_title_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    更新发票抬头信息到数据库
    :param data: 发票抬头字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.invoice_title_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询发票抬头信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, company_id: str) -> tuple[bool, Any|None]:
        tbl_name = self.invoice_title_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query: dict[str, Any] = {}
        if company_id or len(company_id) > 0:
            query['company_id'] = {'$eq': company_id}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, None)
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, InvoiceTitleDao|None]:
        tbl_name = self.invoice_title_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        query = {'_id': ObjectId(id)}
        result, value = self.mongo_impl.query_by_condition(tbl_name, query, None)
        if not result or value is None:
            self.logger.error("No invoice record found with the given ID.")
            return False, None
        dao = InvoiceTitleDao()
        dao.from_db(value[0])
        return True, dao
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.invoice_title_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
