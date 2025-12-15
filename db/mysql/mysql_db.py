
import datetime
import math
from typing import Any
from db.base import DbBaseImpl
from dbutils.pooled_db import PooledDB as pdb  # type: ignore
import MySQLdb as SqlDb

class MySqlImpl(DbBaseImpl):
    def __init__(self):
        super().__init__()
        self.logger.info("MySQL database initialized with host: %s, port: %s", self.mysql_host, self.mysql_port)
        self.dbpool = None
        if self.mysql_host is not None:
            try:
                self.dbpool = pdb(creator=SqlDb,
                        maxconnections=100,
                        host = self.mysql_host,
                        port=int(self.mysql_port),
                        user=self.mysql_username,
                        password=self.mysql_password,
                        database=self.mysql_database,
                        charset="utf8")
            except Exception as err:
                self.logger.error(err)
    def __del__(self):
        if self.dbpool is not None:
            self.dbpool.close()

    def get_connection(self):
        """
        获取数据库连接
        :return: 数据库连接对象
        """
        if self.dbpool is None:
            self.logger.error("Database pool is not initialized.")
            return None
        try:
            conn = self.dbpool.connection()
            return conn
        except Exception as err:
            self.logger.error("Failed to get database connection: %s", err)
            return None
        
    def close_connection(self, conn):
        """
        关闭数据库连接
        :param conn: 数据库连接对象
        """
        if conn is not None:
            try:
                conn.close()
            except Exception as err:
                self.logger.error("Failed to close database connection: %s", err)
    # 
    # 把dict中的keys和values转换成mysql的字段和值
    # key, values的格式为
    # keys = "key1,key2,key3"
    # values = "'value1','value2','value3'"
    # @param {dict} d 字典对象
    # @return {tuple} 返回一个元组，包含keys和values
    #
    def dict_to_insert_sql(self, table: str, data: dict[str, Any]) -> str:
        keys = ",".join(data.keys())
        values = ''
        for item in data.items():
            key = item[0]
            val = item[1]
            if type(val) is str:
                if val == "-":
                    val = "'1970-01-01'" if key == "market_date" else "0.0"
                else:
                    val = "'" + val + "'"
            elif type(val) is datetime.date:
                    if key == "create_date":
                        val = "'" + val.strftime("%Y-%m-%d") + "'"
                    else:
                        val = "'" + val.strftime("%Y-%m-%d %H:%M:%S") + "'"
            elif type(val) is datetime.datetime:
                    val = "'" + val.strftime("%Y-%m-%d %H:%M:%S") + "'"
            elif math.isnan(val):
                val = "NULL"
            else:
                val = str(val)
            if len(values) == 0:
                values = val
            else:
                values = values + "," + val
        insert_sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
        self.logger.debug("insert SQL: %s", insert_sql)
        return insert_sql

    def dict_to_update_sql(self, table: str, data: dict[str, Any], condition: str) -> str:
        setsql = ''
        for item in data.items():
            try:
                key = item[0]
                val = item[1]
                if key == "id":
                    continue
                if type(val) is str:
                    val = "'" + val + "'"
                elif type(val) is datetime.date:
                    val = "'" + val.strftime("%Y-%m-%d") + "'"
                elif type(val) is datetime.datetime:
                    val = "'" + val.strftime("%Y-%m-%d %H:%M:%S") + "'"
                elif math.isnan(val):
                    val = "NULL"
                else:
                    val = str(val)
                if len(setsql) == 0:
                    setsql = key
                else:
                    setsql = setsql + "," + key
                setsql = setsql + "=" + val
            except Exception as err:
                self.logger.error(err)
        if len(setsql) == 0:
            self.logger.error("No valid data to update in table %s", table)
            return ""
        update_sql = f"UPDATE {table} SET {setsql} WHERE {condition}"
        self.logger.debug("Generated SQL: %s", update_sql)
        return update_sql