
import datetime
import math
import logging
from typing import Any
from db.mysql.mysql_db import MySqlImpl
import MySQLdb as SqlDb
from dao.company_dao import CompanyDao

class MySqlCompanyImpl():
    def __init__(self, mysql_impl: MySqlImpl):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.mysql_impl = mysql_impl
        self.company_tbl = 'company_tbl'

    
    """
    添加公司信息到数据库
    :param data: 公司信息字典
    :return: 成功返回True，否则返回False
    """
    def add_company(self, data: dict[str, Any]) -> bool:
        conn = self.mysql_impl.get_connection()
        if conn is None:
            return False
        try:
            tbl_name = self.company_tbl
            insert_sql = self.mysql_impl.dict_to_insert_sql(tbl_name, data)
            cur = conn.cursor()
            cur.execute(insert_sql)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            self.logger.error(f"添加公司信息失败: {e}")
            return False
        finally:
            self.mysql_impl.close_connection(conn)
        
    """ 
    更新公司信息到数据库
    :param data: 公司信息字典
    :param condition: 更新条件，例如 "id = 1"
    :return: 成功返回True，否则返回False
    """
    def update_company(self, data: dict[str, Any], condition: str) -> bool:
        conn = self.mysql_impl.get_connection()
        if conn is None:
            return False
        try:
            tbl_name = self.company_tbl
            update_sql = self.mysql_impl.dict_to_update_sql(tbl_name, data, condition)
            if not update_sql:
                return False
            cur = conn.cursor()
            cur.execute(update_sql)
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            self.logger.error(f"更新公司信息失败: {e}")
            return False
        finally:
            self.mysql_impl.close_connection(conn)

    """
    查询公司信息
    :param condition: 查询条件，例如 "id = 1"
    :return: 查询结果列表，每个元素是一个字典，包含公司信息
    """
    def query_all_company(self, name: str, address: str, contacts: str) -> tuple[bool, None|list[Any]]:
        try:
            db = self.mysql_impl.get_connection()
            if db is None:
                self.logger.error("数据库连接失败")
                return False, None
            tbl_name = self.company_tbl
            filter = []
            if name:
                filter.append(f"name LIKE '%{name}%'")
            if address:
                filter.append(f"address LIKE '%{address}%'")
            if contacts:
                filter.append(f"contacts LIKE '%{contacts}%'")
            filter_sql = " AND ".join(filter)
            if filter_sql:
                query_sql = f"SELECT * FROM {tbl_name} WHERE {filter_sql}"
            else:
                query_sql = f"SELECT * FROM {tbl_name}"
            cur = db.cursor(SqlDb.cursors.DictCursor)
            cur.execute(query_sql)
            ret = cur.fetchall()
            cur.close()
            if not ret:
                return True, []
            return True, ret            
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
        finally:
            self.mysql_impl.close_connection(db)

    """
    function:
    description: 从服务器查询公司信息
    param {*} course
    return {*}
    """
    def query_company_by_id(self, id: int) -> tuple[bool, CompanyDao|None]:
        try:
            db = self.mysql_impl.get_connection()
            if db is None:
                self.logger.error("数据库连接失败")
                return False, None
            tbl_name = self.company_tbl
            query_sql = f"SELECT * FROM {tbl_name} WHERE id = {id}"
            cur = db.cursor(SqlDb.cursors.DictCursor)
            cur.execute(query_sql)
            ret = cur.fetchone()
            cur.close()
            dao = CompanyDao()
            dao.from_db(ret)
            return True, dao
        except Exception as e:
            self.logger.error(f"查询公司信息失败: {e}")
            return False, None
        finally:
            self.mysql_impl.close_connection(db)
    
    """
    function:
    description: 删除公司信息
    param {*} self
    return {*}
    """
    def delete_company(self, id: int) -> bool:
        sql = f"DELETE FROM {self.company_tbl} WHERE id = {id}"
        try:
            conn = self.mysql_impl.get_connection()
            if conn is None:
                self.logger.error("数据库连接失败")
                return False
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
        except Exception as e:
            self.logger.error(f"删除公司信息失败: {e}")
            return False
        finally:
            self.mysql_impl.close_connection(conn)
        return True