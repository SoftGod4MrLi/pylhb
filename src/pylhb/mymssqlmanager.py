"""
模块：mymssqlmanager
作者：李生
描述：Microsoft SQL Server 管理
"""
import os
import re
from datetime import datetime
from .mymssql import MyMSSQL

class MyMSSQLManager:
    """Microsoft SQL Server 管理"""
    def __init__(self, server,port, user, password, database,trusted=False):
        self.server=server
        self.port=port
        self.user=user
        self.password=password
        self.database=database
        self.trusted=trusted

    def create(self,mdfFileName=None,ldfFileName=None,initialSize4MB = 100,maxSize4MB: int = -1,fileGrowth4MB: int = 10) -> tuple[bool,str]:
        """
        创建数据库
        Args:
            mdfFileName：数据文件
            ldfFileName：日志文件
            initialSize4MB：初始大小
            maxSize4MB：最大大小 (MB, -1 表示无限制)
            fileGrowth4MB：文件增长增量 (MB)
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                if mdfFileName and ldfFileName:
                    max_size_clause = "UNLIMITED" if maxSize4MB == -1 else f"{maxSize4MB}MB"
                    sql = f"""
                            CREATE DATABASE [{self.database}]
                            ON PRIMARY 
                            (NAME = N'{self.database}', 
                             FILENAME = N'{mdfFileName}', 
                             SIZE = {initialSize4MB}MB, 
                             MAXSIZE = {max_size_clause}, 
                             FILEGROWTH = {fileGrowth4MB}MB)
                            LOG ON 
                            (NAME = N'{self.database}_log', 
                             FILENAME = N'{ldfFileName}', 
                             SIZE = {initialSize4MB // 4}MB, 
                             MAXSIZE = {max_size_clause}, 
                             FILEGROWTH = {fileGrowth4MB}MB)
                            """
                    (successed,msg)=mssql.exec(sql)
                else:
                    (successed,msg)=mssql.exec(f"CREATE DATABASE [{self.database}]")
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def drop(self) -> tuple[bool,str]:
        """
        删除数据库
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                mssql.restore(f"ALTER DATABASE [{self.database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                (successed,msg)=mssql.exec(f"DROP DATABASE [{self.database}]")
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def attach(self,mdfFileName,ldfFileName) -> tuple[bool,str]:
        """
        附加数据库
        Args:
            mdfFileName：数据文件
            ldfFileName：日志文件
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                (successed,msg)=mssql.exec(f"EXEC sp_attach_db N'{self.database}','{mdfFileName}',N'{ldfFileName}'")
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def detach(self) -> tuple[bool,str]:
        """
        分离数据库
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                mssql.restore(f"ALTER DATABASE [{self.database}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
                (successed,msg)=mssql.exec(f"EXEC sp_detach_db '{self.database}'")
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"
            
    def backup(self,fileFullName) -> tuple[bool,str]:
        """
        备份数据库
        Args:
            fileFullName：绝对路径的备份文件名
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                (successed,msg)=mssql.backup(fileFullName)
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def backupall(self,fileFullName) -> tuple[bool,str]:
        """
        备份所有数据库
        Args:
            fileFullName：绝对路径的备份文件名，文件名不需要，只需要提取路径。
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                databases=mssql.get("SELECT name FROM sys.databases WHERE database_id > 4")
                if databases and len(databases)>0:
                    for db in databases:
                        mssql.Database=db["name"]
                        fileFullName=os.path.join(os.path.dirname(fileFullName),db["name"]+"-"+datetime.now().strftime("%Y%m%d-%H%M%S")+".bak")
                        mssql.backup(fileFullName)
                mssql.close()
                return True,"OK"
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def restore(self,fileFullName) -> tuple[bool,str]:
        """
        恢复数据库
        Args:
            fileFullName：用于恢复的绝对路径的备份文件名
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                (successed,msg)=mssql.restore(fileFullName)
                mssql.close()
                return successed,msg
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"
            
    def delLog(self) -> tuple[bool,str]:
        """
        删除数据库日志
        Returns:
            是否成功
            执行结果
        """
        try:
            mssqlMaster=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            mssqlDB=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successedMaster,msgMaster)=mssqlMaster.connect()
            (successedDB,msgDB)=mssqlDB.connect()
            if successedMaster and successedDB:
                mssqlMaster.exec(f"ALTER DATABASE {self.database} SET RECOVERY SIMPLE WITH NO_WAIT")
                mssqlMaster.exec(f"ALTER DATABASE {self.database} SET RECOVERY SIMPLE")
                mssqlDB.exec("DBCC SHRINKFILE(2, 1)")
                mssqlMaster.exec(f"ALTER DATABASE {self.database} SET RECOVERY FULL WITH NO_WAIT")
                mssqlMaster.exec(f"ALTER DATABASE {self.database} SET RECOVERY FULL")
                return True,"OK"
            else:
                if successedMaster:
                    mssqlMaster.close()
                if successedDB:
                    mssqlDB.close()
                if successedMaster:
                    return False,msgDB
                elif successedDB:
                    return False,msgMaster
                else:
                    return False,msgDB+","+msgMaster
        except Exception as e:
            return False,f"{e}"

    def clearNull(self) -> tuple[bool,str]:
        """
        清除null
        Returns:
            是否成功
            执行结果
        """
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect()
            if successed:
                sql="""
                SELECT O.[Name] AS P_TableName,
                IsNull(C.[name],'') AS P_FieldName,
                IsNull(T.[name],'') As P_Type,
                case when exists(SELECT 1 FROM sysobjects where xtype='PK' and parent_obj=C.id and name in (
                SELECT name FROM sysindexes WHERE indid in(
                SELECT indid FROM sysindexkeys WHERE id = C.id AND colid=C.colid
                ))) then 1 else 0 end As P_PrimaryKey
                FROM syscolumns C  
                LEFT JOIN systypes T  ON C.xtype = T.xusertype
                LEFT JOIN syscomments M ON C.cdefault=M.ID
                LEFT JOIN SysObjects O ON C.id=O.id
                WHERE O.xtype='U'         
                Order By O.[Name],C.colid
                """
                clearedTables=[]
                tables=mssql.get(sql)
                if tables and len(tables)>0:
                    for table in tables:
                        if table["P_PrimaryKey"]==0:
                            if table["P_TableName"] not in clearedTables:
                                clearedTables.append(table["P_TableName"])
                            if table["P_Type"]=="varchar" or table["P_Type"]=="text" or table["P_Type"]=="nvarchar" or table["P_Type"]=="char" or table["P_Type"]=="nchar" or table["P_Type"]=="ntext":
                                mssql.exec(f"UPDATE {table["P_TableName"]} SET {table["P_FieldName"]} = '' WHERE {table["P_FieldName"]} IS NULL")
                            if table["P_Type"]=="int" or table["P_Type"]=="decimal" or table["P_Type"]=="bigint" or table["P_Type"]=="smallint" or table["P_Type"]=="tinyint" or table["P_Type"]=="numeric" or table["P_Type"]=="float" or table["P_Type"]=="real" or table["P_Type"]=="money" or table["P_Type"]=="smallmoney":
                                mssql.exec(f"UPDATE {table["P_TableName"]} SET {table["P_FieldName"]} = 0 WHERE {table["P_FieldName"]} IS NULL")
                return True,"OK"
            else:
                return False,msg
        except Exception as e:
            return False,f"{e}"

    def runSQL(self,fileFullName) -> tuple[bool, str, list]:
        errors=[]
        try:
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect()
            if successed:
                # 读取 SQL 文件
                with open(fileFullName, 'r', encoding='utf-8') as file:
                    sqlContent = file.read()
                # 分割 SQL 语句（按分号分割，需要处理字符串中的分号和注释）
                sqlStatements = self._splitSQL(sqlContent)
                # 遍历执行
                for i, statement in enumerate(sqlStatements, 1):
                    # 跳过空语句
                    if not statement or not statement.strip():
                        continue
                    (successed,msg)=mssql.exec(statement)
                    if successed==False:
                        errors.append(f"执行（{statement}）：{msg}")
                return True,"OK",errors
            else:
                return False,msg,errors
        except Exception as e:
            return False,f"{e}",errors

    def _splitSQL(self,sql_content):
        """
        增强版：根据 GO 关键字拆分，支持 GO {count} 语法
        
        Args:
            sql_content (str): SQL 文件内容
        
        Returns:
            list: SQL 语句列表（如果 GO 带数字，会返回对应数量的重复语句）
        
        Example:
            "INSERT INTO t VALUES(1)\nGO 3" 会返回 3 条相同的 INSERT 语句
        """
        statements = []
        # 按行处理
        lines = sql_content.split('\n')
        current_statement = []
        for line in lines:
            stripped_line = line.strip()
            # 匹配 GO 或 GO 数字（如 GO 10）
            go_match = re.match(r'^GO\s*(\d*)\s*$', stripped_line, re.IGNORECASE)
            go_with_comment_match = re.match(r'^GO\s+(\d+)\s+--', stripped_line, re.IGNORECASE)
            if go_match or go_with_comment_match:
                # 获取执行次数
                if go_match:
                    count_str = go_match.group(1)
                else:
                    count_str = go_with_comment_match.group(1)
                
                count = int(count_str) if count_str else 1
                # 保存当前语句
                if current_statement:
                    statement = '\n'.join(current_statement).strip()
                    if statement:
                        # 如果 count > 1，重复添加语句
                        for _ in range(count):
                            statements.append(statement)
                    current_statement = []
            else:
                # 添加到当前语句
                current_statement.append(line.rstrip('\n'))
        # 处理最后一条语句
        if current_statement:
            statement = '\n'.join(current_statement).strip()
            if statement:
                statements.append(statement)
        return statements

    

    