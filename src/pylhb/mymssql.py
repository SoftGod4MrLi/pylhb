'''
模块：myodbc
作者：李生
描述：通过ODBC操作Microsoft SQL Server数据库，包含连接、创建表、增删改查等操作。
注意：
ODBC Driver 17 for SQL Server下载：
https://learn.microsoft.com/zh-cn/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16
注意，如果是ODBC Driver 18 for SQL Server，那实例化时记得传driver.
'''
import os
import pyodbc
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import platform

class MyMSSQL:
    """MSSQL管理类"""
    def __init__(self,*,server=None,user=None,password=None,database=None,port=1433,timeout=0,autoCommit=False,trusted=False,driver="ODBC Driver 17 for SQL Server",connectStr=None,maxWorker=5):
        """
        MYSQL构造
        Args:
            server：服务器名称
            user：用户
            password：密码
            database：数据库
            port：端口号
            timeout：超时时间
            autoCommit：自动提交
            trusted：信任（Windows身份登录)
            driver：驱动
            maxWorker：最大线程数
        """
        self.server=server
        self.user=user
        self.password=password
        self.database=database
        self.port=port
        self.timeout=timeout
        self.autoCommit=autoCommit
        self.trusted=trusted
        self.driver=driver
        self.conn=None
        self.cursor=None
        self.executor = ThreadPoolExecutor(max_workers=maxWorker)
        self.connectStr=connectStr
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

    def getAllInstances4Windows(self):
        """获取Windows系统里的Microsoft SQL Server实例（通过注册表，所以仅限Windows系统）"""
        if platform.system()=="Windows":
            try:
                import winreg
                instances = []
                reg_path = r"SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL"
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                i = 0
                while True:
                    try:
                        # 枚举键值，每个值代表一个实例
                        instance_name, service_name, _ = winreg.EnumValue(reg_key, i)
                        instances.append({
                            "InstanceName": instance_name,
                            "ServiceName": service_name
                        })
                        i += 1
                    except OSError:
                        # 没有更多实例时跳出循环
                        break
                winreg.CloseKey(reg_key)
                return True,"OK",instances
            except FileNotFoundError:
                return False,"未打到SQL Server实例。",None
        else:
            return False,"仅限Windows调用。",None
        
    def getConnectString(self,useMaster=False) :
        """获取连接字符串"""
        if self.connectStr:
            return self.connectStr;
            
        if useMaster:
            conn_str = f"DRIVER={{{self.driver}}};SERVER={self.server},{self.port};DATABASE=master;"
        else:
            conn_str = f"DRIVER={{{self.driver}}};SERVER={self.server},{self.port};DATABASE={self.database};"
        if self.trusted:
            conn_str += "Trusted_Connection=yes;"
        else:
            if self.user:
                pwd="" if self.password is None else self.password
                conn_str += f"UID={self.user};PWD={pwd};"
            if self.timeout>0:
                conn_str += f"Connection Timeout={self.timeout};"
        return conn_str
            
    async def connect4Async(self):
        """异步连接数据库"""
        return await self.loop.run_in_executor(
            self.executor, 
            self.connect,
        )
        
    def connect(self,useMaster=False):
        """同步连接数据库"""
        try:
            connectString = self.getConnectString(useMaster=useMaster)
            self.conn = pyodbc.connect(connectString,autocommit=self.autoCommit)
            self.cursor=self.conn.cursor()
            return True,"OK"
        except Exception as e:
            self.conn=None
            self.cursor=None
            return False,str(e)
            
    @property
    def Connected(self):
        """获取连接状态"""
        return self.conn is not None
        
    def setAutoCommit(self,autoCommit):
        """设置自动提交"""
        if not self.conn:
            return False,"未连接数据库。"
        try:
            self.conn.autocommit=autoCommit
            return True
        except Exception as e:
            return False
            
    @property
    def IsAutoCommit(self):
        """获取是否自动提交"""
        if self.conn:
            return self.conn.autocommit
        return False

    # getter-服务器名称
    @property
    def Server(self):
        return self.server
    # setter-服务器名称
    @Server.setter
    def Server(self,value):
        self.server=value

    # getter-用户
    @property
    def User(self):
        return self.user
    # setter-用户
    @User.setter
    def User(self,value):
        self.user=value

    # getter-密码
    @property
    def Password(self):
        return self.password
    # setter-密码
    @Password.setter
    def Password(self,value):
        self.password=value

    # getter-端口
    @property
    def Port(self):
        return self.port
    # setter-端口
    @Port.setter
    def Port(self,value):
        self.port=value

    # getter-数据库
    @property
    def Database(self):
        return self.database
    # setter-数据库
    @Database.setter
    def Database(self,value):
        self.database=value

    # getter-超时时间
    @property
    def Timeout(self):
        return self.timeout
    # setter-超时时间
    @Timeout.setter
    def Timeout(self,value):
        self.timeout=value

    # getter-自动提交
    @property
    def AutoCommit(self):
        return self.autoCommit
    # setter-自动提交
    @AutoCommit.setter
    def AutoCommit(self,value):
        self.autoCommit=value

    # getter-是否信任（Windows身份登录)
    @property
    def Trusted(self):
        return self.trusted
    # setter-是否信任（Windows身份登录)
    @Trusted.setter
    def Trusted(self,value):
        self.trusted=value

    # getter-驱动
    @property
    def Driver(self):
        return self.driver
    # setter-驱动
    @Driver.setter
    def Driver(self,value):
        self.driver=value

    # getter-连接字符串
    @property
    def ConnectStr(self):
        return self.connectStr
    # setter-连接字符串
    @ConnectStr.setter
    def ConnectStr(self,value):
        self.connectStr=value

    async def backup4Async(self, fileFullName, showProcess=False):
        """
        异步备份数据库
        Args:
            fileFullName：备份绝对路径文件名
            showProcess：是否显示时度提示
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.backup,
            fileFullName,
            showProcess
        )

    def backup(self,fileFullName,showProcess=False):
        """
        备份数据库
        Args:
            fileFullName：备份绝对路径文件名
            showProcess：是否显示时度提示
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            sql = f"""
            BACKUP DATABASE [{self.database}] TO DISK = '{fileFullName}'
            """
            self.cursor.execute(sql)
            # 等待执行进度
            while self.cursor.nextset():
                if self.cursor.description:
                    rows = self.cursor.fetchall()
                    for row in rows:
                        if hasattr(row, 'Percent_Complete'):
                            if showProcess:
                                print(f"备份进度: {row.Percent_Complete}%")
            return (True,"OK")
        except Exception as e:
            return (False,str(e))

    async def restore4Async(self,fileFullName,showProcess=False):
        """
        异步恢复数据库
        Args:
            fileFullName：备份绝对路径文件名
            showProcess：是否显示时度提示
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.restore,
            fileFullName,
            showProcess
        )

    def restore(self,fileFullName,showProcess=False):
        """
        恢复数据库
        Args:
            fileFullName：备份绝对路径文件名
            showProcess：是否显示时度提示
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            # 查杀此数据库的连接进程
            self.cursor.execute(f"ALTER DATABASE [{self.database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
            sql = f"""
            RESTORE DATABASE [{self.database}] FROM DISK = '{fileFullName}' WITH REPLACE
            """
            self.cursor.execute(sql)
            # 等待执行进度
            while self.cursor.nextset():
                if self.cursor.description:
                    rows = self.cursor.fetchall()
                    for row in rows:
                        if hasattr(row, 'Percent_Complete'):
                            if showProcess:
                                print(f"恢复进度: {row.Percent_Complete}%")
            return (True,"OK")
        except Exception as e:
            return (False,str(e))
        
    async def insert4Async(self, tableName: str, data: dict):
        """
        异步插入记录
        Args:
            tableName：表名
            data：数据字典
        Returns:
            是否成功
            执行结果
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
            tableName：表名
            data：数据字典
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            columns = ", ".join(data.keys())
            values = tuple(data.values())
            sql = f"INSERT INTO {tableName} ({columns}) VALUES {values}"
            self.cursor.execute(sql)
            return (True,"OK")
        except Exception as e:
            return (False,str(e))
            
    async def update4Async(self, table_name: str, data: dict, where: str, params: tuple[Any]):
        """
        异步修改记录
        Args:
            tableName：表名
            data：数据字典
            where：条件
            params：条件参数值
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.update,
            table_name,
            data,
            where,
            params
        )
        
    def update(self, tableName: str, data: dict, where: str, params: tuple[Any]):
        """
        修改记录
        Args:
            tableName：表名
            data：数据字典
            where：条件
            params：条件参数值
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
            values = tuple(data.values()) + params
            sql = f"UPDATE {tableName} SET {set_clause} WHERE {where}"
            self.cursor.execute(sql, values)
            return (True,"OK")
        except Exception as e:
            return (False,str(e))
        
    async def delete4Async(self, tableName: str, where: str, params: tuple[Any]):
        """
        异步删除记录
        Args:
            tableName：表名
            where：条件
            params：条件参数值
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
        
    def delete(self, tableName: str, where: str, params: tuple[Any]):
        """
        删除记录
        Args:
            tableName：表名
            where：条件
            params：条件参数值
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            sql = f"DELETE FROM {tableName} WHERE {where}"
            self.cursor.execute(sql, params)
            return (True,"OK")
        except Exception as e:
            return (False,str(e))

    async def exists4Async(self,sql):
        """
        异步检查是否存在
        Args:
            sql：SQL语句
        Returns:
            是否成功
            执行结果
            是否存在
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.exists,
            sql
        )
            
    def exists(self,sql):
        """
        检查是否存在
        Args:
            sql：SQL语句
        Returns:
            是否成功
            执行结果
            是否存在
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。",False
        try:
            self.cursor.execute(sql)
            row = self.cursor.fetchone()
            exists = exists = row is not None and row[0] > 0
            return True,"OK",exists
        except Exception as e:
            return False,str(e),False
            
    async def select4Async(self, tableName, columns: tuple[str] | None = None, where=None, params: tuple[Any] | None=None,toDict=True):
        """
        异步查询数据
        Args:
            tableName：表名
            columns：列
            where：条件
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
            tableName,
            columns,
            where,
            params,
            toDict
        )
        
    def select(self, tableName, columns: tuple[str] | None = None, where=None, params: tuple[Any] | None=None,toDict=True):
        """
        查询数据
        Args:
            tableName：表名
            columns：列
            where：条件
            params：条件参数值
            toDict：结果是否转为字典
        Returns:
            是否成功
            执行结果
            字典/列表
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。",None
        try:
            cols = "*" if columns is None else ", ".join(columns)
            sql = f"SELECT {cols} FROM {tableName}"
            if where:
                sql += f" WHERE {where}"
            print(sql)
            if where and params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            if toDict:
                # 获取列名
                descs: list[str] | None = [column[0] for column in self.cursor.description]
                # 转换为字典列表
                if descs:
                    data = []
                    for row in self.cursor.fetchall():
                        data.append(dict(zip(descs, row)))
                    return True,"OK",data
                else:
                    data = self.cursor.fetchall()
                    return True,"OK",data
            else:
                data = self.cursor.fetchall()
                return True,"OK",data
        except Exception as e:
            return False,str(e),None
            
    async def get4Async(self,sql,toDict=True):
        """
        异步查询数据
        Args:
            sql：SQL语句
            toDict：结果是否转为字典
        Returns:
            字典/列表
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.get,
            sql,
            toDict
        )
            
    def get(self,sql,toDict=True):
        """
        查询数据
        Args:
            sql：SQL语句
            toDict：结果是否转为字典
        Returns:
            字典/列表
        """
        if not self.conn or not self.cursor:
            return None
        try:
            self.cursor.execute(sql)
            if toDict:
                # 获取列名
                columns = [column[0] for column in self.cursor.description]
                # 转换为字典列表
                results = []
                for row in self.cursor.fetchall():
                    results.append(dict(zip(columns, row)))
                return results
            else:
                return self.cursor.fetchall()
        except:
            return None

    async def exec4Async(self,sql):
        """
        异步执行SQ
        Args:
            sql：SQL语句
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.exec,
            sql
        )
        
    def exec(self,sql):
        """
        执行SQL
        Args:
            sql：SQL语句
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return False,"未连接数据库。"
        try:
            self.cursor.execute(sql)
            return (True,"OK")
        except Exception as e:
            return (False,str(e))

    async def execProc4Async(self,procName,params: tuple[Any] | None = None):
        """
        异步执行存储过程
        Args:
            procName：存储过程名称
            params：参数
        Returns:
            是否成功
            执行结果
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.execProc,
            procName,
            params
        )
        
    def execProc(self,procName,params: tuple[Any] | None = None):
        """
        执行存储过程
        Args:
            procName：存储过程名称
            params：参数
        Returns:
            是否成功
            执行结果
        """
        if not self.conn or not self.cursor:
            return (False,"未连接数据库。")
        try:
            if params:
                placeholders = ', '.join(['?' for _ in params])
                sql = f"EXEC {procName} {placeholders}"
                self.cursor.execute(sql, params)
            else:
                sql = f"EXEC {procName}"
                self.cursor.execute(sql)
            return (True,"OK")
        except Exception as e:
            return (False,str(e))

    async def execProcGet4Async(self,procName,params: list[Any] | None = None):
        """
        异步执行存储过程
        Args:
            procName：存储过程名称
            params：参数
        Returns:
            是否成功
            执行结果
            数据
        """
        return await self.loop.run_in_executor(
            self.executor, 
            self.execProcGet,
            procName,
            params
        )
        
    def execProcGet(self,procName,params: list[Any] | None = None):
        """
        执行存储过程并返回数据
        Args:
            procName：存储过程名称
            params：参数
        Returns:
            是否成功
            执行结果
            数据
        """
        if not self.conn or not self.cursor:
            return (False,"未连接数据库。",None)
        try:
            if params:
                placeholders = ', '.join(['?' for _ in params])
                sql = f"EXEC {procName} {placeholders}"
                self.cursor.execute(sql, params)
            else:
                sql = f"EXEC {procName}"
                self.cursor.execute(sql)
                
            datas = []
            if self.cursor.description:
                columns = [desc[0] for desc in self.cursor.description]
                for row in self.cursor.fetchall():
                    datas.append(dict(zip(columns, row)))
                    
            return (True,"OK",datas)
        except Exception as e:
            return (False,str(e),None)

    def commit(self):
        """提交事务"""
        if not self.conn or not self.cursor:
            return
        if self.conn.autocommit==True:
            return
        self.conn.commit()

    def rollback(self):
        """回滚事务"""
        if not self.conn or not self.cursor:
            return
        self.conn.rollback()

    def close(self):
        """关闭连接"""
        if self.cursor:
            self.cursor.close()
            self.cursor=None
        if self.conn:
            self.conn.close()
            self.conn=None