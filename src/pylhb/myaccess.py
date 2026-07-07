"""
模块：myaccess
作者：李生
描述：Microsoft Access 数据库操作类
"""
import pyodbc
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

class MyAccess:
    """
    Microsoft Access 数据库操作类（支持密码）
    支持 .mdb 和 .accdb，自动适配驱动，提供事务集成及连接检测。
    """
    def __init__(self, dbPath: str, password: str | None = None,autoCommit=False, driver: str | None = None,maxWorker=5):
        """
        初始化 Access 数据库连接
        :param dbPath: 数据库文件完整路径
        :param password: 数据库密码（若无则传 None 或空字符串）
        :param driver: ODBC 驱动名称，不指定则自动查找
        """
        self.dbPath = dbPath
        self.password = password
        self.driver = driver or self._findDriver()
        self.connection: pyodbc.Connection | None = None
        self.cursor: pyodbc.Cursor | None = None
        self.autoCommit=autoCommit
        self.executor = ThreadPoolExecutor(max_workers=maxWorker)
        self.loop = asyncio.get_event_loop()

    @staticmethod
    def _findDriver() -> str:
        """
        自动查找可用的 Access ODBC 驱动（优先最新版本）
        需要安装Microsoft Access ODBC 驱动，请安装 Access Database Engine。
        """
        drivers = [d for d in pyodbc.drivers() if 'Access' in d]
        if drivers:
            # 1. 优先查找支持 .accdb 的驱动（最准确）
            for d in drivers:
                if 'Access' in d and 'accdb' in d:
                    return d
            # 2. 如果没有找到，查找包含 'Access' 的驱动（兼容旧版 .mdb）
            for d in drivers:
                if 'Access' in d:
                    return d
            # 3. 实在找不到，返回默认值（虽然连接时大概率会失败）
            return "Microsoft Access Driver (*.mdb, *.accdb)"
        return "Microsoft Access Driver (*.mdb, *.accdb)"

    def _buildConnectionString(self, exclusive: bool = False) -> str:
        """
        构建 ODBC 连接字符串
        Args:
            exclusive: 是否以独占模式打开
        """
        connectString = f'DRIVER={{{self.driver}}};DBQ={self.dbPath};'
        if self.password:
            connectString += f'PWD={self.password};'
        if exclusive:
            connectString += 'Exclusive=1;'
        return connectString

    def connect(self, exclusive: bool = False):
        """
        建立数据库连接
        Args:
            exclusive: 是否以独占模式打开（默认共享）
        """
        try:
            connectString = self._buildConnectionString(exclusive)
            self.connection = pyodbc.connect(connectString,autocommit=self.autoCommit)
            self.cursor = self.connection.cursor()
            return True,"OK"
        except Exception as e:
            self.connection=None
            self.cursor=None
            return False,str(e)

    def close(self) -> None:
        """关闭连接和游标"""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def isExclusive(self) -> bool:
        """
        检测数据库是否被其他程序以独占模式打开
        Return:
            返回 True 表示被独占，False 表示未被独占（或可共享连接）
        """
        try:
            # 尝试独占连接（先关闭现有连接避免冲突）
            if self.connection:
                self.close()
            testConnect = pyodbc.connect(self._buildConnectionString(exclusive=True), timeout=2)
            testConnect.close()
            return False
        except pyodbc.Error as e:
            errorMsg = str(e).lower()
            if 'exclusive' in errorMsg or 'already in use' in errorMsg or 'cannot open' in errorMsg:
                return True
            return False

    def testConnection(self) -> tuple[bool, str]:
        """
        测试数据库连接是否正常（快速诊断）
        返回: (是否成功, 状态描述)
        """
        try:
            conn = pyodbc.connect(self._buildConnectionString(exclusive=False), timeout=2)
            conn.close()
            return True, "连接成功"
        except pyodbc.Error as e:
            return False, str(e)

    async def select4Async(self,sql: str, params: tuple | list | None = None,toDict=True):
        """
        异步查询数据
        Args:
            sql：SQL语句
            params：条件参数值
            toDict：结果是否转为字典
        Returns:
            是否成功
            执行结果
            字典/列表
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.select,
            sql,
            params,
            toDict
        )

    def select(self, sql: str, params: tuple | list | None = None,toDict=True) :
        """
        查询数据
        Args:
            sql：SQL语句
            params：条件参数值
            toDict：结果是否转为字典
        Returns:
            是否成功
            执行结果
            字典/列表
        """
        if not self.cursor:
            return False,"未连接数据库。",None
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            rows = self.cursor.fetchall()
            if not toDict:
                return rows
            columns = [desc[0] for desc in self.cursor.description]
            return True,"OK",[dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return False,f"查询失败: {e}",None

    async def insert4Async(self, table: str, data: dict[str, Any]):
        """
        异步插入数据
        Args：
            table：表名
            data：数据
        Return:
            是否成功
            信息
            爱影响行数
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.insert,
            table,
            data
        )

    def insert(self, table: str, data: dict[str, Any]):
        """
        插入数据
        Args：
            table：表名
            data：数据
        Return:
            是否成功
            信息
            爱影响行数
        """
        if not self.cursor:
            return False,"未连接数据库。",None
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?'] * len(data))
            sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            if list(data.values()):
                self.cursor.execute(sql, list(data.values()))
            else:
                self.cursor.execute(sql)
            return True,"OK",self.cursor.rowcount
        except Exception as e:
            return False,f"插入数据失败: {e}",0

    async def update4Async(self, table: str, data: dict[str, Any],whereClause: str, whereParams: tuple | list | None = None):
        """
        异步插入数据
        Args：
            table：表名
            data：数据
        Return:
            是否成功
            信息
            爱影响行数
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.update,
            table,
            data,
            whereClause,
            whereParams
        )
        
    def update(self, table: str, data: dict[str, Any],whereClause: str, whereParams: tuple | list | None = None):
        """
        更新数据
        Args:
            table: 表名
            data: 字段-新值字典
            whereClause: WHERE 条件，例如 "id = ?"
            whereParams: WHERE 条件的参数值
        Return:
            是否成功
            信息
            爱影响行数
        """
        if not self.cursor:
            return False,"未连接数据库。",None
        try:
            set_clause = ', '.join([f"{k}=?" for k in data.keys()])
            sql = f"UPDATE {table} SET {set_clause} WHERE {whereClause}"
            params = list(data.values())
            if whereParams:
                params.extend(whereParams)
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            return True,"OK",self.cursor.rowcount
        except Exception as e:
            return False,f"更新数据失败: {e}",0
        
    async def delete4Async(self, table: str, whereClause: str, whereParams: tuple | list | None = None):
        """
        异步删除数据
        Args：
            table：表名
            data：数据
            whereClause: WHERE 条件，例如 "id = ?"
            whereParams: WHERE 条件的参数值
        Return:
            是否成功
            信息
            爱影响行数
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.delete,
            table,
            whereClause,
            whereParams
        )
        
    def delete(self, table: str, whereClause: str, whereParams: tuple | list | None = None):
        """
        删除数据
        Args：
            table：表名
            data：数据
            whereClause: WHERE 条件，例如 "id = ?"
            whereParams: WHERE 条件的参数值
        Return:
            是否成功
            信息
            爱影响行数
        """
        if not self.cursor:
            return False,"未连接数据库。",0
        try:
            sql = f"DELETE FROM {table} WHERE {whereClause}"
            if whereParams:
                self.cursor.execute(sql, whereParams)
            else:
                self.cursor.execute(sql)
            return True,"OK",self.cursor.rowcount
        except Exception as e:
            return False,f"删除数据失败: {e}",0

    def useTransaction(self) -> None:
        """开启手动事务（关闭自动提交）"""
        if self.connection:
            self.connection.autocommit = False

    def commit(self) -> None:
        """提交当前事务"""
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        """回滚当前事务"""
        if self.connection:
            self.connection.rollback()

