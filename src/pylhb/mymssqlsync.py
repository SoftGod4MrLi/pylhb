"""
模块：mymssqlsync
作者：李生
描述：Microsoft SQL Server同步
"""
from .mymssql import MyMSSQL
from .myspinner import SpinnerStyle,MySpinner
from typing import Dict, List, Tuple

class MyMSSQLSync():
    """
    Microsoft SQL Server同步类
    """
    def __init__(self, sourceMSSQL:MyMSSQL,targetMSSQL:MyMSSQL,syncTables=True,syncPrimaryKeys=False,syncIndexes=True,syncForeignKeys=True,syncFunctions=True,syncViews=True,syncTriggers=True,syncProcedures=True,deleteExtraTables=True,deleteExtraColumns=True):
        """
        构造函数
        Args：
            sourceMSSQL：源数据库的MyMSSQL对象
            targetMSSQL：目标数据库的MyMSSQL对象
            syncTables：是否同步表，默认True
            syncPrimaryKeys：是不同步主键，默认False，因为同步表时会创建主键，所以这个默认就不要同步了
            syncIndexes：是否同步索引，默认True
            syncForeignKeys：是否同步外键，默认True
            syncFunctions：是否同步函数，默认True
            syncViews：是否同步视图，默认True
            syncProcedures：是否同步存储过程，默认True
            deleteExtraTables：是否删除目标库里多余的表
            deleteExtraColumns：是否删除目标库里表的多余的字段
        """
        self.sourceMSSQL=sourceMSSQL
        self.targetMSSQL=targetMSSQL
        self.syncTables=syncTables
        self.syncPrimaryKeys=syncPrimaryKeys
        self.syncIndexes=syncIndexes
        self.syncForeignKeys=syncForeignKeys
        self.syncFunctions=syncFunctions
        self.syncViews=syncViews
        self.syncTriggers=syncTriggers
        self.syncProcedures=syncProcedures
        self.deleteExtraTables=deleteExtraTables
        self.deleteExtraColumns=deleteExtraColumns
        # 存储生成的同步SQL
        self.syncSQLs: List[str] = []
        # 执行同步SQL错误列表
        self.syncErrors:List[str] = []

    # ================== 1.基本函数 ==================
    def addSQL(self,sql):
        """
        添加SQL到脚本列表
        Args：
            sql：SQL脚本
        """
        self.syncSQLs.append(sql.strip() + "\n")
    
    def getAllTables(self,mssql:MyMSSQL):
        """
        获取所有用户表
        Args:
            mssql：MyMSSQL对象
        """
        sql=f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE = 'BASE TABLE' AND TABLE_SCHEMA = 'dbo'
            ORDER BY TABLE_NAME
        """
        tables=mssql.get(sql)
        return [row["TABLE_NAME"] for row in tables]

    def getTableColumns(self,mssql:MyMSSQL,tableName):
        """
        获取表的列
        Args:
            mssql：MyMSSQL对象
            tableName：表名
        """
        sql=f"""
            SELECT 
                COLUMN_NAME, DATA_TYPE, IS_NULLABLE, 
                CHARACTER_MAXIMUM_LENGTH, NUMERIC_PRECISION, NUMERIC_SCALE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = '{tableName}' AND TABLE_SCHEMA = 'dbo'
            ORDER BY ORDINAL_POSITION
        """
        return mssql.get(sql)

    def getPrimaryKeys(self,mssql:MyMSSQL,tableName):
        """
        获取表的主键
        Args:
            mssql：MyMSSQL对象
            tableName：表名
        """
        sql=f"""
            SELECT c.COLUMN_NAME
            FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS pk
            JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE c 
                ON pk.CONSTRAINT_NAME = c.CONSTRAINT_NAME
            WHERE pk.TABLE_NAME = '{tableName}' AND pk.CONSTRAINT_TYPE = 'PRIMARY KEY'
            ORDER BY c.ORDINAL_POSITION
        """
        tablePrimaryKeys=mssql.get(sql)
        return [row["COLUMN_NAME"] for row in tablePrimaryKeys]

    def getIndexes(self,mssql:MyMSSQL,tableName):
        """
        获取表的索引
        Args:
            mssql：MyMSSQL对象
            tableName：表名
        """
        indexes = []
        sql=f"""
            SELECT DISTINCT
                i.name AS index_name,
                i.type_desc AS index_type,
                i.is_unique AS is_unique
            FROM sys.indexes i
            JOIN sys.tables t ON i.object_id = t.object_id
            WHERE t.name = '{tableName}' AND i.type > 0 AND i.is_primary_key = 0
        """
        tableIndexes=mssql.get(sql)
        # 遍历索引取索引的列
        for idx in tableIndexes:
            idxName=idx["index_name"]
            sql=f"""
                SELECT col.name
                FROM sys.index_columns ic
                JOIN sys.columns col ON ic.object_id = col.object_id AND ic.column_id = col.column_id
                JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                WHERE i.name = '{idxName}' AND OBJECT_NAME(ic.object_id) = '{tableName}'
                ORDER BY ic.key_ordinal
            """
            indexColumns=mssql.get(sql)
            cols = [row["name"] for row in indexColumns]
            indexes.append({
                "name": idxName,
                "columns": cols,
                "unique": idx["is_unique"],
                "type": idx["index_type"]
            })
        return indexes;

    def getForeignKeys(self,mssql:MyMSSQL,tableName):
        """
        获取表的外键
        Args:
            mssql：MyMSSQL对象
            tableName：表名
        """
        sql=f"""
            SELECT 
                fk.name AS fk_name,
                OBJECT_NAME(fk.parent_object_id) AS parent_table,
                c1.name AS parent_column,
                OBJECT_NAME(fk.referenced_object_id) AS ref_table,
                c2.name AS ref_column
            FROM sys.foreign_keys fk
            JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
            JOIN sys.columns c1 ON fkc.parent_object_id = c1.object_id AND fkc.parent_column_id = c1.column_id
            JOIN sys.columns c2 ON fkc.referenced_object_id = c2.object_id AND fkc.referenced_column_id = c2.column_id
            WHERE OBJECT_NAME(fk.parent_object_id) = '{tableName}'
        """
        return mssql.get(sql)

    def getObjectDefinition(self,mssql:MyMSSQL,objName):
        """
        获取视图/存储过程/触发器/函数的创建脚本
        Args:
            mssql：MyMSSQL对象
            objName：名称
        """
        try:
            sql=f"SELECT definition FROM sys.sql_modules WHERE object_id = OBJECT_ID('{objName}')"
            defScript=mssql.get(sql)
            return defScript[0]["definition"] if defScript else ""
        except:
            return ""

    def getAllObjects(self,mssql:MyMSSQL,objType):
        """
        获取所有视图/存储过程/触发器/函数
        Args:
            mssql：MyMSSQL对象
            objType：类型
        """
        query_map = {
            "VIEW": "SELECT name FROM sys.views WHERE schema_id = SCHEMA_ID('dbo')",
            "PROCEDURE": "SELECT name FROM sys.procedures WHERE schema_id = SCHEMA_ID('dbo')",
            "TRIGGER": "SELECT name FROM sys.triggers WHERE parent_class = 1",
            "FUNCTION": """
                SELECT name 
                FROM sys.objects 
                WHERE type IN ('FN', 'IF', 'TF') AND schema_id = SCHEMA_ID('dbo')
            """ 
        }
        objects=mssql.get(query_map[objType])
        return [row["name"] for row in objects]

    def getColumnDefinition(self, col):
        """
        获取字段所有类型长度/精度问题
        支持：varchar/nvarchar/char/nchar/binary/varbinary/numeric/decimal
        """
        dataType = col["DATA_TYPE"]
        charLen = col.get("CHARACTER_MAXIMUM_LENGTH")
        precision = col.get("NUMERIC_PRECISION")
        scale = col.get("NUMERIC_SCALE")

        # 字符串 + 二进制类型（带长度）
        if dataType in ["varchar", "nvarchar", "char", "nchar", "binary", "varbinary"]:
            if charLen == -1:
                return f"{dataType}(MAX)"
            else:
                return f"{dataType}({charLen})"

        # 数值精度类型（带精度+小数位）
        elif dataType in ["numeric", "decimal"]:
            return f"{dataType}({precision},{scale})"

        # 其他类型直接返回
        else:
            return dataType

    def getTableCreateSQL(self,tableName):
        """
        获取表的外键
        Args:
            tableName：表名
        """
        """生成建表 SQL（含主键）"""
        columns = self.getTableColumns(self.sourceMSSQL, tableName)
        pkCols = self.getPrimaryKeys(self.sourceMSSQL, tableName)

        colSQL = []
        for col in columns:
            nullSQL = "NULL" if col["IS_NULLABLE"] == "YES" else "NOT NULL"
            dt = col["DATA_TYPE"]
            if dt in ["varchar", "nvarchar", "char"]:
                size = col["CHARACTER_MAXIMUM_LENGTH"]
                dt = f"{dt}({size if size != -1 else 'MAX'})"
            colSQL.append(f"[{col['COLUMN_NAME']}] {dt} {nullSQL}")

        if pkCols:
            pkSQL = ", ".join([f"[{c}]" for c in pkCols])
            colSQL.append(f"CONSTRAINT PK_{tableName} PRIMARY KEY ({pkSQL})")

        createSQL = f"CREATE TABLE [{tableName}] (\n  " + ",\n  ".join(colSQL) + "\n)"
        self.addSQL(createSQL)

    def syncTableColumns(self,tableName):
        """
        同步现有表：新增/修改/删除字段 
        Args:
            tableName：表名
        """
        sourceCols = self.getTableColumns(self.sourceMSSQL, tableName)
        targetCols = self.getTableColumns(self.targetMSSQL, tableName)
        sourceColsNames = [c["COLUMN_NAME"] for c in sourceCols]
        targetColsNames = [c["COLUMN_NAME"] for c in targetCols]

        # 删除旧库多余字段
        if self.deleteExtraColumns:
            for col in targetCols:
                if col["COLUMN_NAME"] not in sourceColsNames:
                    self.addSQL(f"ALTER TABLE [{tableName}] DROP COLUMN [{col['COLUMN_NAME']}]")

        # 新增或修改字段
        for col in sourceCols:
            if col["COLUMN_NAME"] not in targetColsNames:
                nullCond = "NULL" if col["IS_NULLABLE"] == "YES" else "NOT NULL"
                colType = self.getColumnDefinition(col)
                self.addSQL(f"ALTER TABLE [{tableName}] ADD [{col['COLUMN_NAME']}] {colType} {nullCond}")
                
    def syncTablePrimaryKeys(self,tableName):
        """
        同步表主键
        Args:
            tableName：表名
        """
        sourcePKs = self.getPrimaryKeys(self.sourceMSSQL, tableName)
        targetPKs = self.getPrimaryKeys(self.targetMSSQL, tableName)

        if sourcePKs and sourcePKs != targetPKs:
            if targetPKs:
                self.addSQL(f"ALTER TABLE [{tableName}] DROP CONSTRAINT PK_{tableName}")
            pkStr = ", ".join([f"[{col}]" for col in sourcePKs])
            self.addSQL(f"ALTER TABLE [{tableName}] ADD CONSTRAINT PK_{tableName} PRIMARY KEY ({pkStr})")

    def syncTableForeignKeys(self,tableName):
        """
        同步表外键
        Args:
            tableName：表名
        """
        sourceFKs = self.getForeignKeys(self.sourceMSSQL, tableName)
        targetFKs = self.getForeignKeys(self.targetMSSQL, tableName)
        targetFKNames = [fk["fk_name"] for fk in targetFKs]

        for fk in sourceFKs:
            fk_name = fk["fk_name"]
            if fk_name not in targetFKNames:
                sql = f"""
                ALTER TABLE [{fk['parent_table']}] 
                ADD CONSTRAINT [{fk_name}] 
                FOREIGN KEY ([{fk['parent_column']}]) 
                REFERENCES [{fk['ref_table']}] ([{fk['ref_column']}])
                """
                self.addSQL(sql)

    def syncTableIndexes(self,tableName):
        """
        同步表索引
        Args:
            tableName：表名
        """
        sourceIndexes = self.getIndexes(self.sourceMSSQL, tableName)
        targetIndexes = self.getIndexes(self.targetMSSQL, tableName)
        targetIDXNames = [idx["name"] for idx in targetIndexes]

        for idx in sourceIndexes:
            if idx["name"] not in targetIDXNames:
                unique = "UNIQUE" if idx["unique"] else ""
                cols = ", ".join([f"[{col}]" for col in idx["columns"]])
                self.addSQL(f"CREATE {unique} INDEX [{idx['name']}] ON [{tableName}] ({cols})")
    
    # ================== 2.生成同步SQL ==================
    def syncTableStructure(self):
        """
        同步同步表 + 字段 + 主键 + 索引 + 外键
        """
        sourceTables = self.getAllTables(self.sourceMSSQL)
        targetTables = self.getAllTables(self.targetMSSQL)

        # 1.删除旧库多余的表
        if self.deleteExtraTables:
            for table in targetTables:
                if table not in sourceTables:
                    self.addSQL(f"DROP TABLE IF EXISTS [{table}]")
        # 2.新增表
        for table in sourceTables:
            if table not in targetTables:
                self.getTableCreateSQL(table)
        # 3.同步现有表：新增/修改/删除字段 
        for table in set(sourceTables) & set(targetTables):
            self.syncTableColumns(table)

        # 同步表的主键/外键/索引
        for table in sourceTables:
            if self.syncPrimaryKeys:
                self.syncTablePrimaryKeys(table)
            if self.syncTableForeignKeys:
                self.syncTableForeignKeys(table)
            if self.syncTableIndexes:
                self.syncTableIndexes(table)

    def syncAllViews(self):
        """
        同步视频
        """
        sourceViews = self.getAllObjects(self.sourceMSSQL, "VIEW")
        targetViews = self.getAllObjects(self.targetMSSQL, "VIEW")

        for view in sourceViews:
            definition = self.getObjectDefinition(self.sourceMSSQL, view)
            if view in targetViews:
                self.addSQL(f"DROP VIEW IF EXISTS [{view}]")
            self.addSQL(definition)

    def syncAllFunctions(self):
        """
        同步函数
        """
        sourceFuncs = self.getAllObjects(self.sourceMSSQL, "FUNCTION")
        targetFuncs = self.getAllObjects(self.targetMSSQL, "FUNCTION")

        for func in sourceFuncs:
            definition = self.getObjectDefinition(self.sourceMSSQL, func)
            if func in targetFuncs:
                self.addSQL(f"DROP FUNCTION IF EXISTS [{func}]")
            self.addSQL(definition)

    def syncAllProcedures(self):
        """
        同步存储过程
        """
        sourceProcs = self.getAllObjects(self.sourceMSSQL, "PROCEDURE")
        targetProcs = self.getAllObjects(self.targetMSSQL, "PROCEDURE")

        for proc in sourceProcs:
            definition = self.getObjectDefinition(self.sourceMSSQL, proc)
            if proc in targetProcs:
                self.addSQL(f"DROP PROCEDURE IF EXISTS [{proc}]")
            self.addSQL(definition)
            
    def syncAllTriggers(self):
        """
        同步触发器
        """
        sourceTriggers = self.getAllObjects(self.sourceMSSQL, "TRIGGER")
        targetTriggers = self.getAllObjects(self.targetMSSQL, "TRIGGER")

        for trig in sourceTriggers:
            definition = self.getObjectDefinition(self.sourceMSSQL, trig)
            if trig in targetTriggers:
                self.addSQL(f"DROP TRIGGER IF EXISTS [{trig}]")
            self.addSQL(definition)

    def executeSyncSQL(self) -> tuple[bool,str]:
        """
        执行更新脚本
        """
        try:
            for sql in self.syncSQLs:
                try:
                    (successed,msg) = self.targetMSSQL.exec(sql)
                    if not successed:
                        self.syncErrors.append(f"执行SQL错误：{msg}\n脚本如下：\n{sql}\n")
                except Exception as e:
                    self.syncErrors.append(f"执行SQL错误：{e}\n脚本如下：\n{sql}\n")
            self.targetMSSQL.commit()
            return (True,"同步完成。")
        except Exception as e:
            self.targetMSSQL.rollback()
            return (False,f"同步失败（已回滚）：{e}")

    def getSyncSQL(self):
        """
        生成同步脚本
        """
        # 清空SQL列表
        self.syncSQLs.clear()
        # 清空错误列表
        self.syncErrors.clear()

        # 重新生成更新脚本
        # 同步顺序：表 → 视图 → 函数 → 存储过程 → 触发器
        if self.syncTables:
            self.syncTableStructure()
        if self.syncViews:
            self.syncAllViews()
        if self.syncFunctions:
            self.syncAllFunctions()
        if self.syncProcedures:
            self.syncAllProcedures()
        if self.syncTriggers:
            self.syncAllTriggers()
        
        return (self.syncSQLs,self.syncErrors)

    def saveToFile(self,syncLists:List[str],fileName):
        """
        将SQL列表或错误列表保存到文件
        """
        with open(fileName, 'w', encoding='utf-8') as f:
            for str in syncLists:
                f.write(str)
        
    def goSync(self):
        """
        同步
        """
        spinner = MySpinner(SpinnerStyle.BRAILLE, "准备就绪...")
        spinner.start()
        # 清空SQL列表
        self.syncSQLs.clear()
        # 清空错误列表
        self.syncErrors.clear()

        # 重新生成更新脚本
        # 同步顺序：表 → 视图 → 函数 → 存储过程 → 触发器
        if self.syncTables:
            spinner.setText("正在生成表同步脚本...")
            self.syncTableStructure()
        if self.syncViews:
            spinner.setText("正在生成视图同步脚本...")
            self.syncAllViews()
        if self.syncFunctions:
            spinner.setText("正在生成函数同步脚本...")
            self.syncAllFunctions()
        if self.syncProcedures:
            spinner.setText("正在生成存储过程同步脚本...")
            self.syncAllProcedures()
        if self.syncTriggers:
            spinner.setText("正在生成触发器同步脚本...")
            self.syncAllTriggers()

        # 执行更新脚本
        spinner.setText("正在执行同步脚本（可能需要一点时间，请耐心等待）...")
        (successed,msg)=self.executeSyncSQL()
        if successed:
            spinner.stop(msg)
        else:
            spinner.stop(msg)

        # 列出错误列表
        if len(self.syncErrors)>0: 
            print("\n错误列表：\n")
            for err in self.syncErrors:
                print(err)
        
    
        