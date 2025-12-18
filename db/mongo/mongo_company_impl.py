'''
Author: liguoqiang
Date: 2021-08-06 14:10:41
LastEditors: liguoqiang
LastEditTime: 2025-09-18 17:00:23
Description: 
'''
# coding="utf8"

from pymongo.collection import Collection
import logging
from typing import Any
from bson.objectid import ObjectId
from dao.company_dao import CompanyDao
from dao.company_bank_account_dao import CompanyBankAccountDao
from db.mongo.mongo_impl import MongoImpl
import re

class MongoCompanyImpl():
    def __init__(self, mongo_impl: MongoImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mongo_impl = mongo_impl


    # 公司信息表名
    def company_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['company_tbl']
    # 公司银行账户表名
    def company_bank_account_tbl(self) -> None|Collection:
        if self.mongo_impl.db is None:
            self.logger.error("MongoDB connection is not established.")
            return None
        return self.mongo_impl.db['company_bank_account_tbl']
    
    """
    添加公司信息到数据库
    :param data: 公司信息字典
    :return: 成功返回True，否则返回False
    """
    def add_company(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        tbl_name = self.company_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        return self.mongo_impl.add(tbl_name, data)
    
    def query_same_company(self, name: str, brief_name: str) -> tuple[bool, None|list[Any]]:
        tbl_name = self.company_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        query: dict[str, Any] = {}
        name = re.escape(name)
        query['$or'] = [
            {'name': {'$regex': name, '$options': 'i'}},
            {'brief_name': {'$regex': name, '$options': 'i'}}
        ]
        # query['name'] = {'$regex': name, '$options': 'i'}
        # query['brief_name'] = {'$regex': brief_name, '$options': 'i'}
        return self.mongo_impl.query_by_condition(tbl_name, query, None)
        
    """ 
    更新公司信息到数据库
    :param data: 公司信息字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_company(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        tbl_name = self.company_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False
        return self.mongo_impl.update(tbl_name, data, condition)
        
    """
    查询公司信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_company(self, name: str, address: str, contacts: str, company_type: str) -> tuple[bool, None|list[Any]]:
        tbl_name = self.company_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        query: dict[str, Any] = {}
        if name or len(name) > 0:
            name = re.escape(name)
            query['$or'] = [
                {'name': {'$regex': name, '$options': 'i'}},
                {'brief_name': {'$regex': name, '$options': 'i'}}
            ]
        if address or len(address) > 0:
            query['address'] = {'$regex': address, '$options': 'i'}
        if contacts or len(contacts) > 0:
            query['contacts'] = {'$regex': contacts, '$options': 'i'}
        if company_type or len(company_type) > 0:
            query['company_type'] = {'$regex': company_type, '$options': 'i'}
        return self.mongo_impl.query_by_condition(tbl_name, query, {'brief_name': 1})
    
    """
    查询内部公司信息 type 不等于 2
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_inner_company(self, name: str, address: str, contacts: str, company_type: str) -> tuple[bool, None|list[Any]]:
        """
        查询内部公司信息
        :return: 成功返回True和公司信息字典，否则返回False和空字典
        """
        tbl_name = self.company_tbl()
        if tbl_name is None:
            self.logger.error("Company table not found in MongoDB.")
            return False, None
        condition: dict[str, Any] = {}
        if name or len(name) > 0:
            name = re.escape(name)
            condition['$or'] = [
                {'name': {'$regex': name, '$options': 'i'}},
                {'brief_name': {'$regex': name, '$options': 'i'}}
            ]
            # condition['name'] = {'$regex': name, '$options': 'i'}
            # condition['brief_name'] = {'$regex': name, '$options': 'i'}
        if address or len(address) > 0:
            condition['address'] = {'$regex': address, '$options': 'i'}
        if contacts or len(contacts) > 0:
            condition['contacts'] = {'$regex': contacts, '$options': 'i'}
        if company_type or len(company_type) > 0:
            condition['company_type'] = {'$regex': company_type, '$options': 'i'}
        # 只查询公司类型不是2的记录
        condition['type'] = {'$ne': 2}
        return self.mongo_impl.query_by_condition(tbl_name, condition, {'name': 1})
    
    """
    function:
    description: 从服务器查询公司信息
    param {*} course
    return {*}
    """
    def query_company_by_id(self, id: str) -> tuple[bool, CompanyDao|None]:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False, None
            query = {'_id': ObjectId(id)}
            result = tbl_name.find_one(query)
            if result is None:
                return False, None
            company_dao = CompanyDao()
            company_dao.from_db(result)
            return True, company_dao
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
        
    def query_company_by_brief_name(self, brief_name: str) -> tuple[bool, CompanyDao|None]:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False, None
            query = {'brief_name': {'$eq': brief_name}}
            result = tbl_name.find_one(query)
            if result is None:
                return False, None
            company_dao = CompanyDao()
            company_dao.from_db(result)
            return True, company_dao
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
        
    """
    function:
    description: 删除公司信息
    param {*} self
    return {*}
    """
    def delete_company(self, id: str) -> bool:
        try:
            tbl_name = self.company_tbl()
            if tbl_name is None:
                self.logger.error("Company table not found in MongoDB.")
                return False
            query = {'_id': ObjectId(id)}
            ret = tbl_name.delete_one(query)
            return ret.deleted_count > 0  # 返回是否有记录被删除
        except Exception as e:
            self.logger.error(f"删除公司信息失败: {e}")
            return False

    """
    function: add_company_bank_account
    description: 增加公司银行账户信息
    param {dict[str, Any]} data: 公司银行账户信息字典
    param {*} self
    return {*}
    """
    def add_company_bank_account(self, data: dict[str, Any]) -> tuple[bool, str|None]:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False, None
            if 'id' in data:
                del data['id']
            return self.mongo_impl.add(tbl_name, data)
        except Exception as e:
            self.logger.error(f"添加公司银行账户信息失败: {e}")
            return False, None
        
    """ 
    更新公司银行账户到数据库
    :param data: 公司银行账户信息字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_company_bank_account(self, data: dict[str, Any], condition: dict[str, Any]) -> bool:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False
            if 'id' in data:
                del data['id']
            return self.mongo_impl.update(tbl_name, data, condition)
        except Exception as e:
            self.logger.error(f"更新公司银行账户信息失败: {e}")
            return False
        
    """
    查询公司银行账户信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_company_bank_account(self, company_id: str) -> tuple[bool, None|list[CompanyBankAccountDao]]:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False, None
            query = {}
            if company_id or len(company_id) > 0:
                query['company_id'] = {'$eq': company_id}
            
            results = list(tbl_name.find(query))
            dao_list = []
            for result in results:
                # 将查询结果转换为 CompanyDao 对象
                dao = CompanyBankAccountDao()
                dao.from_db(result)
                dao_list.append(dao)
            return True, dao_list
        except Exception as e:
            self.logger.error(f"查询公司银行账户信息失败: {e}")
            return False, None
        
    def query_company_bank_account_by_id(self, id: str) -> tuple[bool, CompanyBankAccountDao|None]:
        tbl_name = self.company_bank_account_tbl()
        if tbl_name is None:
            self.logger.error("Company bank account table not found in MongoDB.")
            return False, None
        query = {'_id': ObjectId(id)}
        result, value = self.mongo_impl.query_by_condition(tbl_name, query, None)
        if not result or value is None:
            return False, None
        dao = CompanyBankAccountDao()
        dao.from_db(value[0])
        return True, dao
    """
    function:
    description: 删除公司银行账户信息
    param {*} self
    return {*}
    """
    def delete_company_bank_account(self, id: str) -> bool:
        try:
            tbl_name = self.company_bank_account_tbl()
            if tbl_name is None:
                self.logger.error("Company bank account table not found in MongoDB.")
                return False
            query = {'_id': ObjectId(id)}
            ret = tbl_name.delete_one(query)
            return ret.deleted_count > 0  # 返回是否有记录被删除
        except Exception as e:
            self.logger.error(f"删除公司银行账户信息失败: {e}")
            return False