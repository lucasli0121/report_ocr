'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2024-06-06 21:00:51
Description: 
'''
# coding="utf8"

from typing import Any
from bson import ObjectId
from pymongo import MongoClient, ReadPreference, WriteConcern
from pymongo.collection import Collection
import logging
from db.base import DbBaseImpl
from copy import deepcopy

class MongoImpl(DbBaseImpl):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        if self.mongo_host is not None:
            self.conn = MongoClient(
                host = self.mongo_host,
                port=int(self.mongo_port),
                w="majority",
                read_preference=ReadPreference.PRIMARY,
                username=self.mongo_username,
                password=self.mongo_password,
                authSource=self.mongo_database)
            self.db = self.conn[self.mongo_database]

    def __del__(self):
        if self.conn is not None:
            self.conn.close()


    # 公司银行账户表名
    def company_bank_account_tbl(self) -> None|Collection:
        if self.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.db['company_bank_account']
    
    # 公司开票记录表名
    def company_invoice_record_tbl(self) -> None|Collection:
        if self.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.db['company_invoice_record']
    
    """
    添加
    :param data: 信息字典
    :return: 成功返回True，否则返回False
    """
    def add(self, table: Collection, data: dict[str, Any]) -> tuple[bool, str|None]:
        try:
            if table is None:
                self.logger.error("table not found in MongoDB.")
                return False, None
            data = dict(data)
            data.pop('id', None)  # 移除'id'字段，MongoDB会自动生成'_id'
            ret = table.insert_one(data)
            return ret.acknowledged, str(ret.inserted_id)  # 确认插入操作已被确认
        except Exception as e:
            self.logger.error(f"添加信息失败: {e}")
            return False, e.args[0]
        
    """ 
    更新到数据库
    :param data: 字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update(self, table: Collection, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        try:
            if table is None:
                self.logger.error("table not found in MongoDB.")
                return False
            data = deepcopy(data)
            if len(condition) == 0:
                condition = {'_id': ObjectId(data.get('id', ''))}  # 如果没有条件，使用id作为默认条件
            else:
                condition = deepcopy(condition)
                if 'id' in condition:
                    condition['_id'] = ObjectId(condition['id'])
                    del condition['id']
            if 'id' in data:
                del data['id']
            ret = table.update_one(condition, {'$set': data})
            return ret.matched_count > 0  # 返回是否有记录被修改
        except Exception as e:
            self.logger.error(f"更新信息失败: {e}")
            return False
        
    """
    查询信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_by_condition(self, table: Collection, condition: dict[str, Any], sort: dict[str, Any]|None ) -> tuple[bool, Any]:
        try:
            if table is None:
                self.logger.error("table not found in MongoDB.")
                return False, None
            
            if sort is not None and len(sort) > 0:
                # 执行排序查询
                results = list(table.find(condition).collation({'locale':'zh', 'strength':1}).sort(sort))
                return True, results if results else None
            else:
                # 执行查询
                results = list(table.find(condition))
                return True, results if results else None
        except Exception as e:
            self.logger.error(f"查询信息失败: {e}")
            return False, None
    
    """
    function:
    description: 删除
    param {*} self
    return {*}
    """
    def delete(self, table: Collection, condition: dict[str, Any]) -> bool:
        try:
            if table is None:
                self.logger.error("table not found in MongoDB.")
                return False
            ret = table.delete_one(condition)
            return ret.deleted_count > 0  # 返回是否有记录被删除
        except Exception as e:
            self.logger.error(f"删除失败: {e}")
            return False