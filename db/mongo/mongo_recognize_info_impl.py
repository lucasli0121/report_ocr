'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 19:35:46
Description: 
'''
# coding="utf8"

from datetime import datetime, timedelta
from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.recognize_info_dao import RecognizeInfoDao, RecognizeResult, RecognizeType
from db.mongo.mongo_impl import MongoImpl

class MongoRecognizeInfoImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 表名
    def recognize_info_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['recognize_info_tbl']
    
    
    """
    添加识别信息到数据库
    :param data: 
    :return: 成功返回True，否则返回False
    """
    def add(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
        
    """ 
    :param data: 
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all(self, type:int) -> tuple[bool, Any|None]:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("invoice table not found in MongoDB.")
            return False, None
        query: dict[str, Any] = {}
        begin_time = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query['create_time'] = {'$gte': begin_time}
        query['create_time']['$lte'] = end_time
        if type != RecognizeType.AllType.value:
            query['type'] = type
        # 执行查询
        return self.mongo_impl.query_by_condition(tbl_name, query, {'create_time': -1})
    
    
    """
    function:
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_by_id(self, id: str) -> tuple[bool, RecognizeInfoDao|None]:
        tbl_name = self.recognize_info_tbl()
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
        dao = RecognizeInfoDao()
        dao.from_db(value[0])
        return True, dao

    """
    function: 查询正在识别的记录
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_recognizing_list_by_type(self, type: int) -> tuple[bool, Any|None]:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        query = {'result': RecognizeResult.InProgress.value}
        if type != RecognizeType.AllType.value:
            query['type'] = type
        return self.mongo_impl.query_by_condition(tbl_name, query, None)
    """
    function: 查询等待识别的记录
    description: 从服务器查询信息
    param {*} course
    return {*}
    """
    def query_waiting_list_by_type(self, type: int) -> tuple[bool, Any|None]:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        query = {'result': RecognizeResult.Waiting.value}
        if type != RecognizeType.AllType.value:
            query['type'] = type
        return self.mongo_impl.query_by_condition(tbl_name, query, None)
    """
    function:
    description: 删除信息
    param {*} self
    return {*}
    """
    def delete(self, id: str) -> bool:
        tbl_name = self.recognize_info_tbl()
        if tbl_name is None:
            self.logger.error("Invoice table not found in MongoDB.")
            return False
        query = {'_id': ObjectId(id)}
        return self.mongo_impl.delete(tbl_name, query)
