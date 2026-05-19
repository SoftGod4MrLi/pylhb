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
    def __init__(self, dbName: str = "data.db",maxWorker=5):
        self.dbName = dbName
        self.connection = None
        self.cursor = None
        self.executor = ThreadPoolExecutor(max_workers=maxWorker)
        self.loop = asyncio.get_event_loop()
    
    async def connect4Async(self):
        """异步连接数据库"""
        return await self.loop.run_in_executor(
            self.executor, 
            self.connect,
        )
        
    def connect(self):
        """连接数据库"""
        try:
            self.connection = sqlite3.connect(self.dbName)
            self.cursor = self.connection.cursor()
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
        if not self.connection:
            self.connect()
        cols = ", ".join([f"{name} {defn}" for name, defn in columns.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {tableName} ({cols})"
        try:
            self.cursor.execute(sql)
            self.connection.commit()
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
        if not self.connection:
            self.connect()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())
        sql = f"INSERT INTO {tableName} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True,self.cursor.lastrowid
        except sqlite3.Error as e:
            return False,None
    
    async def select4Async(self, tableName: str, columns: List[str] = None, where: str = None, params: Tuple[Any] = None):
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
        
    def select(self, tableName: str, columns: List[str] = None, where: str = None, params: Tuple[Any] = None):
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
        if not self.connection:
            self.connect()
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
        if not self.connection:
            self.connect()
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values()) + params
        sql = f"UPDATE {tableName} SET {set_clause} WHERE {where}"
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
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
        if not self.connection:
            self.connect()
        sql = f"DELETE FROM {tableName} WHERE {where}"
        try:
            self.cursor.execute(sql, params)
            self.connection.commit()
            return True,"OK"
        except sqlite3.Error as e:
            return False,str(e)
    
    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
            self.cursor=None
        if self.connection:
            self.connection.close()
            self.connect=None