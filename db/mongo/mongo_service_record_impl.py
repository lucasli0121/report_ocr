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
from dao.service_record_dao import ServiceRecordDao
from db.mongo.mongo_impl import MongoImpl

class MongoServiceRecordImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 业务表名
    def service_record_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['service_record_tbl']
    
    
    """
    添加记录
    :param data: 信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.service_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    更新信息到数据库
    :param data: 字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.service_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询记录信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典
    """
    def query_all(self, from_company_id: str, to_company_id: str, status: int, begin_time: str, end_time: str) -> tuple[bool, Any|None]:
        tbl_name = self.service_record_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query: dict[str, Any] = {}
        if from_company_id or len(from_company_id) > 0:
            query['from_company_id'] = {'$eq': from_company_id}
        if to_company_id or len(to_company_id) > 0:
            query['to_company_id'] = {'$eq': to_company_id}
        if status > 0:
            query['status'] = {'$eq': status}
        if begin_time or len(begin_time) > 0:
            query['create_time'] = {'$gte': begin_time}
        if end_time or len(end_time) > 0:
            query['create_time'] = {'$lte': end_time}
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, None)
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, ServiceRecordDao|None]:
        tbl_name = self.service_record_tbl()
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
        dao = ServiceRecordDao()
        dao.from_db(value[0])
        return True, dao
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.service_record_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
