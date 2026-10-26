"""本模块提供了一个数据库客户端类，用于与 MySQL 数据库进行交互。"""

import pymysql
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

from utils.LoggerManager import LoggerManager


class DataBaseClient:
    """数据库客户端类，用于管理 MySQL 数据库连接和执行 SQL 操作。"""

    def __init__(self, host: str, user: str, password: str, database: str, port: int = 3306):
        """初始化数据库连接参数并建立连接。

        Args:
            host (str): 数据库地址。
            user (str): 用户名。
            password (str): 密码。
            database (str): 数据库名称。
            port (int, optional): 端口号，默认为 3306。
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.logger = LoggerManager().get_logger()

        self.connection = self.connect()

    def connect(self):
        """建立数据库连接。

        Returns:
            pymysql.connections.Connection: 数据库连接对象。

        Raises:
            pymysql.MySQLError: 数据库连接失败时抛出异常。
        """
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            self.logger.debug("Database connected successfully...")
            return connection
        except pymysql.MySQLError as e:
            self.logger.error(f"Error connecting to MySQL: {e}")
            raise

    def disconnect(self):
        """关闭数据库连接。"""
        if self.connection:
            self.connection.close()
            self.logger.debug("Database connection closed.")

    @contextmanager
    def get_cursor(self):
        """获取数据库游标，支持上下文管理器。

        Yields:
            pymysql.cursors.Cursor: 数据库游标对象。
        """
        if not self.connection:
            self.connect()
        cursor = self.connection.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_query(self, sql: str, params: Optional[Any] = None) -> List[Dict[str, Any]]:
        """执行查询语句。

        Args:
            sql (str): SQL 查询语句。
            params (Optional[Any], optional): SQL 参数，默认为 None。

        Returns:
            List[Dict[str, Any]]: 查询结果列表，每个元素为字典形式。
        """
        self.logger.debug(f'sql:{sql}, params:{params}')
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_update(self, sql: str, params: Optional[Any] = None) -> int:
        """执行更新语句（INSERT/UPDATE/DELETE）。

        Args:
            sql (str): SQL 更新语句。
            params (Optional[Any], optional): SQL 参数，默认为 None。

        Returns:
            int: 受影响的行数。
        """
        self.logger.debug(f'sql:{sql}, params:{params}')
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            self.connection.commit()
            return cursor.rowcount

    @contextmanager
    def transaction(self):
        """事务管理，支持上下文管理器。

        Raises:
            Exception: 事务执行过程中出现异常时回滚事务并抛出异常。
        """
        if not self.connection:
            self.connect()
        try:
            yield
            self.connection.commit()
            self.logger.debug("Transaction committed.")
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Transaction rolled back due to error: {e}")
            raise

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """插入数据。

        Args:
            table (str): 表名。
            data (Dict[str, Any]): 插入的数据，字典形式。

        Returns:
            int: 受影响的行数。
        """
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        return self.execute_update(sql, tuple(data.values()))

    def update(self, table: str, data: Dict[str, Any], condition: str,
               condition_params: Optional[Any] = None) -> int:
        """更新数据。

        Args:
            table (str): 表名。
            data (Dict[str, Any]): 更新的数据，字典形式。
            condition (str): 更新条件。
            condition_params (Optional[Any], optional): 更新条件的参数，默认为 None。

        Returns:
            int: 受影响的行数。
        """
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        params = tuple(data.values())
        if condition_params:
            if isinstance(condition_params, tuple):
                params += condition_params
            elif isinstance(condition_params, dict):
                params += tuple(condition_params.values())
        return self.execute_update(sql, params)

    def delete(self, table: str, condition: str,
               condition_params: Optional[Any] = None) -> int:
        """删除数据。

        Args:
            table (str): 表名。
            condition (str): 删除条件。
            condition_params (Optional[Any], optional): 删除条件的参数，默认为 None。

        Returns:
            int: 受影响的行数。
        """
        sql = f"DELETE FROM {table} WHERE {condition}"
        return self.execute_update(sql, condition_params)

    def select(
            self,
            table: str,
            columns: Optional[List[str]] = None,
            condition: Optional[str] = None,
            condition_params: Optional[Any] = None,
            order_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查询数据。

        Args:
            table (str): 表名。
            columns (Optional[List[str]], optional): 查询的列，默认为所有列。
            condition (Optional[str], optional): 查询条件，默认为 None。
            condition_params (Optional[Any], optional): 查询条件的参数，默认为 None。
            order_by (Optional[str], optional): 排序条件，例如 "age ASC" 或 "name DESC"，默认为 None。

        Returns:
            List[Dict[str, Any]]: 查询结果列表，每个元素为字典形式。
        """
        # 构建查询列
        columns_str = ", ".join(columns) if columns else "*"

        # 构建 SQL 查询语句
        sql = f"SELECT {columns_str} FROM {table}"

        # 添加查询条件
        if condition:
            sql += f" WHERE {condition}"

        # 添加排序条件
        if order_by:
            sql += f" ORDER BY {order_by}"

        # 执行查询并返回结果
        return self.execute_query(sql, condition_params)
