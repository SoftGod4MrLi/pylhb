"""
模块：mysqlite
作者：李生
描述：SQLite数据库管理，包含连接、创建表、增删改查等操作。
"""
import sqlite3
from typing import List, Tuple, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MySQLite:
    """SQLite管理类"""
    def __init__(self, dbName: str = "data.db",autoCommit=False,maxWorker=5):
        self.dbName = dbName
        self.autoCommit=autoCommit
        self.conn = None
        self.cursor = None
        self.executor = ThreadPoolExecutor(max_workers=maxWorker)
        self.loop = asyncio.get_event_loop()

    def __enter__(self) -> None:
        # 进入with块时：自动连接数据库
        self.connect()
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 离开with块时：根据是否异常进行拉交与回滚，然后断开数据库连接
        if self.conn:
            if self.autoCommit==False:
                if exc_type:
                    # 如果发生了异常，撤销本次操作 (回滚)
                    self.conn.rollback()
                else:
                    # 如果没有异常，正式写入数据库 (提交)
                    self.conn.commit()
            # 无论如何，都要关闭游标和连接，释放资源
            self.close()
        
        # 返回 False 表示不吞没异常，让外部也能捕获到错误
        return False
    
    async def connect4Async(self):
        """异步连接数据库"""
        return await self.loop.run_in_executor(
            self.executor, 
            self.connect,
        )
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.dbName,autocommit=self.autoCommit)
            self.cursor = self.conn.cursor()
            return True,"OK"
        except sqlite3.Error as e:
            return False,str(e)
            
    async def createTable4Async(self, tableName: str, columns: dict):
        """
        异步创建表
        Args:
            tableName：列名
            columns：列
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.createTable,
            tableName,
            columns
        )
    
    def createTable(self, tableName: str, columns: dict):
        """
        创建表
        Args:
            tableName：列名
            columns：列
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        cols = ", ".join([f"{name} {defn}" for name, defn in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {tableName} ({cols})"
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return True,"OK"
        except sqlite3.Error as e:
            return False,str(e)
            
    async def insert4Async(self, tableName: str, data: dict):
        """
        异步插入记录
        Args:
            tableName：列名
            data：数据
        Returns:
            是否成功
            最大自增ID
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.insert,
            tableName,
            data
        )
    
    def insert(self, tableName: str, data: dict):
        """
        插入记录
        Args:
            tableName：列名
            data：数据
        Returns:
            是否成功
            最大自增ID
        """
        if not self.conn or not self.cursor:
            return False,None
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        sql = f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True,self.cursor.lastrowid
        except sqlite3.Error as e:
            return False,None
    
    async def select4Async(self, tableName: str, columns: List[str] | None = None, where: str | None = None, params: Tuple[Any] | None = None):
        """
        异步查询数据
        Args:
            tableName：列名
            columns：列
            where：条件
            params：条件参数
        Returns:
            是否成功
            数据列表
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.select,
            tableName,
            columns,
            where,
            params
        )
        
    def select(self, tableName: str, columns: List[str] | None = None, where: str | None = None, params: Tuple[Any] | None = None):
        """
        查询数据
        Args:
            tableName：列名
            columns：列
            where：条件
            params：条件参数
        Returns:
            是否成功
            数据列表
        """
        if not self.conn or not self.cursor:
            return False,[]
        cols = "*" if columns is None else ", ".join(columns)
        sql = f"SELECT {cols} FROM {tableName}"
        if where:
            sql += f" WHERE {where}"
        try:
            if where and params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return True,results
        except sqlite3.Error as e:
            return False,[]
    
    async def update4Async(self, tableName: str, data: dict, where: str, params: Tuple[Any]):
        """
        异步更新数据
        Args:
            tableName：列名
            data：修改字典
            where：条件
            params：条件参数
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.update,
            tableName,
            data,
            where,
            params
        )
        
    def update(self, tableName: str, data: dict, where: str, params: Tuple[Any]):
        """
        更新数据
        Args:
            tableName：列名
            data：修改字典
            where：条件
            params：条件参数
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + params
        sql = f"UPDATE {tableName} SET {set_clause} WHERE {where}"
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True,"OK"
        except sqlite3.Error as e:
            return False,str(e)
    
    async def delete4Async(self, tableName: str, where: str, params: Tuple[Any]):
        """
        异步删除数据
        Args:
            tableName：列名
            where：条件
            params：条件参数
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.delete,
            tableName,
            where,
            params
        )
        
    def delete(self, tableName: str, where: str, params: Tuple[Any]):
        """
        删除数据
        Args:
            tableName：列名
            where：条件
            params：条件参数
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        sql = f"DELETE FROM {tableName} WHERE {where}"
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True,"OK"
        except sqlite3.Error as e:
            return False,str(e)

    def commit(self) -> None:
        """提交当前事务"""
        if self.conn:
            self.conn.commit()

    def rollback(self) -> None:
        """回滚当前事务"""
        if self.conn:
            self.conn.rollback()
            
    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
            self.cursor=None
        if self.conn:
            self.conn.close()
            self.conn=None