from nt import truncate
import os
import platform
from datetime import datetime

from pyodbc import SQL_SERVER_NAME, getDecimalSeparator
from .mymssqlmanager import MyMSSQLManager
from .mydevice import MyDevice
from .myspinner import SpinnerStyle,MySpinner
from .mymssql import MyMSSQL
from .myiis import MyIIS
import subprocess
import getpass
import webbrowser

def showVersion():
    """显示版本号"""
    try:
        from importlib.metadata import version, PackageNotFoundError
        # 直接从包元数据获取版本号
        ver = version("pylhb")
        print(f"pylhb {ver}")
    except PackageNotFoundError:
        print("Package not found.")
    except ImportError:
        print("Import errored.")
    except:
        print("Other errored.")

def showDeviceInfos():
    """显示设备信息"""
    d=MyDevice()
    print(f"系统: {platform.system()} {platform.release()}")
    print(f"系统版本: {platform.version()}")
    print(f"架构: {platform.machine()}")
    print(f"处理器: {platform.processor()}")
    print(f"主机名: {platform.node()}")
    print(f"IP地址: {d.getLocalIP()}")
    print(f"设备ID: {d.getDeviceID()}")
    print(f"Python版本: {platform.python_version()}")

def convertStr2Int(number,defaultValue:int=0) -> int:
    try:
        return int(number)
    except:
        return defaultValue

def checkAndCreatePath(path) -> bool:
    """
    检查文件夹是否存在，不存时就创建
    Args：
        path：路径
    Return：
        是否成功
    """
    if path=="":
        return
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        return True
    except Exception as e:
        return False

class MyMSSQLDo:
    """Microsoft SQL Server 处理"""
    def __init__(self, server ="127.0.0.1",port=1433, user="sa", password="", database ="master",trusted=False):
        self.server=server
        self.port=port
        self.user=user
        self.password=password
        self.database=database
        self.trusted=trusted

    def openSSMS(self):
        """打开SSMS"""
        smsPaths=[r"C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\SSMS.exe",
            r"C:\Program Files (x86)\Microsoft SQL Server Management Studio 20\Common7\IDE\SSMS.exe",
            r"C:\Program Files (x86)\Microsoft SQL Server Management Studio 19\Common7\IDE\SSMS.exe",
            r"C:\Program Files (x86)\Microsoft SQL Server Management Studio 18\Common7\IDE\SSMS.exe",
            r"C:\Program Files\Microsoft SQL Server\100\Tools\Binn\VSShell\Common7\IDE\SSMS.exe",
            r"C:\Program Files\Microsoft SQL Server\90\Tools\Binn\VSShell\Common7\IDE\SSMS.exe"
        ]
        opened=False
        for path in smsPaths:
            if os.path.exists(path):
                os.startfile(path)
                subprocess.Popen(path)
                opened=True
                break
        if not opened:
            print("未找到SSMS程序。")

    def create(self,mdfFileName=None,ldfFileName=None,initialSize4MB = 100,maxSize4MB: int = -1,fileGrowth4MB: int = 10):
        """
        创建数据库
        Args:
            mdfFileName：数据文件
            ldfFileName：日志文件
            initialSize4MB：初始大小
            maxSize4MB：最大大小 (MB, -1 表示无限制)
            fileGrowth4MB：文件增长增量 (MB)
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在创建中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.create(mdfFileName,ldfFileName,initialSize4MB,maxSize4MB,fileGrowth4MB)
            if successed:
                sp.stop("创建成功。")
            else:
                sp.stop(f"创建失败：{msg}",False)
        except Exception as e:
            sp.stop(f"创建失败：{e}",False)
            
    def backup(self,fileFullName):
        """
        备份数据库
        Args:
            fileFullName：绝对路径的备份文件名
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在备份中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.backup(fileFullName)
            if successed:
                sp.stop("备份成功。")
            else:
                sp.stop(f"备份失败：{msg}",False)
        except Exception as e:
            sp.stop(f"备份失败：{e}",False)

    def backupall(self,fileFullName):
        """
        备份所有数据库
        Args:
            fileFullName：绝对路径的备份文件名，文件名不需要，只需要提取路径。
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "准备备份")
        sp.start()
        try:
            sp.setText("正在读取数据库列表...")
            mssql=MyMSSQL(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,autoCommit=True,trusted=self.trusted)
            (successed,msg)=mssql.connect(useMaster=True)
            if successed:
                databases=mssql.get("SELECT name FROM sys.databases WHERE database_id > 4")
                if databases and len(databases)>0:
                    for db in databases:
                        sp.setText(f"正在备份数据库（{db["name"]}）……")
                        mssql.Database=db["name"]
                        fileFullName=os.path.join(os.path.dirname(fileFullName),db["name"]+"-"+datetime.now().strftime("%Y%m%d-%H%M%S")+".bak")
                        mssql.backup(fileFullName)
                mssql.close()
                sp.stop("备份完成。")
            else:
                sp.stop(f"备份失败：{msg}",False)
        except Exception as e:
            sp.stop(f"备份失败：{e}",False)

    def restore(self,fileFullName):
        """
        恢复数据库
        Args:
            fileFullName：用于恢复的绝对路径的备份文件名
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在恢复中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.restore(fileFullName)
            if successed:
                sp.stop(f"恢复成功。")
            else:
                sp.stop(f"恢复失败：{msg}",False)
        except Exception as e:
            sp.stop(f"恢复失败：{e}",False)
            
    def delLog(self):
        """
        删除数据库日志
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在删除中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.delLog()
            if successed:
                sp.stop("删除成功。")
            else:
                sp.stop(f"删除失败：{msg}",False)
        except Exception as e:
            sp.stop(f"删除失败：{e}",False)

    def clearNull(self):
        """
        清除null
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在清除中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.clearNull()
            if successed:
                sp.stop("清除成功。")
            else:
                sp.stop(f"清除失败：{msg}",False)
        except Exception as e:
            sp.stop(f"清除失败：{e}",False)

    def attach(self,mdfFileName,ldfFileName):
        """
        附加数据库
        Args:
            mdfFileName：数据文件
            ldfFileName：日志文件
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在附加中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.attach(mdfFileName,ldfFileName)
            if successed:
                sp.stop("附加成功。")
            else:
                sp.stop(f"附加失败：{msg}",False)
        except Exception as e:
            sp.stop(f"附加失败：{e}",False)

    def detach(self):
        """
        分离数据库
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在分离中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.detach()
            if successed:
                sp.stop("分离成功。")
            else:
                sp.stop(f"分离失败：{msg}",False)
        except Exception as e:
            sp.stop(f"分离失败：{e}",False)

    def drop(self):
        """
        删除数据库
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在删除中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.drop()
            if successed:
                sp.stop("删除成功。")
            else:
                sp.stop(f"删除失败：{msg}",False)
        except Exception as e:
            sp.stop(f"删除失败：{e}",False)

    def runSQL(self,sql):
        """
        执行SQL脚本
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在执行中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg)=mssql.runSQL(sql)
            if successed:
                sp.stop("执行成功。")
            else:
                sp.stop(f"执行失败：{msg}",False)
        except Exception as e:
            sp.stop(f"执行失败：{e}",False)

    def runSQLFile(self,fileFullName,userSQLCMD):
        """
        执行SQL文件
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在执行中...")
        sp.start()
        try:
            mssql=MyMSSQLManager(server=self.server,port=self.port,user=self.user,password=self.password,database=self.database,trusted=self.trusted)
            (successed,msg,errors)=mssql.runSQLFile(fileFullName,userSQLCMD)
            if successed:
                sp.stop("执行成功。")
            else:
                sp.stop(f"执行失败：{msg}",False)
            # 输出错误日志
            if len(errors)>0:
                print("错误：")
                for error in errors:
                    print(error)
        except Exception as e:
            sp.stop(f"执行失败：{e}",False)

    def intputBase(self) -> bool:
        try:
            print("配置基础参数[6]：")
            self.server=input("1.服务器名称（默认为127.0.0.1）: ")
            if not self.server:
                self.server="127.0.0.1"
            port=convertStr2Int(input("2.端口号（默认1433）："),1433)
            if port==0:
                self.port=1433
            self.user=input("3.用户（默认sa）：")
            if not self.user:
                self.user="sa"

            useMW=input("4.使用明文密码（Y/N，默认N）：")
            if not useMW:
                useMW="N"
            if useMW.upper()=="Y":
                self.password=input("5.密码：")
            else:
                self.password=getpass.getpass("5.密码：")
            trust=input("6.用Windows身份验证（Y/N，默认N）：")
            if not trust:
                trust="N"
            if trust.upper()=="Y":
                self.trusted=True
            else:
                self.trusted=False
            return True
        except:
            print("\n>> 错误：输入无效！")
            return False
        
    def showMenu(self):
        print("\n" + "=" * 30)
        print("🌺🌺系统菜单")
        print("=" * 30)
        print("1.创建数据库")
        print("2.附加数据库")
        print("3.分离数据库")
        print("4.备份数据库")
        print("5.备份所有数据库")
        print("6.恢复数据库")
        print("7.删除日志")
        print("8.清除NULL")
        print("9.执行SQL")
        print("10.执行SQL文件")
        print("11.打开SSMS")
        print("0.退出程序")
        print("=" * 30)
        
    def choiceDo(self,choice)->bool:
        match(choice):
            case 1:
                print("👉创建数据库[3]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    mdfFile=input("2.数据文件（空为默认）：")
                    ldfFile=input("3.日志文件（空为默认）：")
                    if mdfFile and ldfFile:
                        self.create(mdfFile,ldfFile)
                    else:
                        self.create()
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 2:
                print("👉附加数据库[3]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    mdfFile=input("2.数据文件：")
                    ldfFile=input("3.日志文件：")
                    if mdfFile and ldfFile:
                        self.create(mdfFile,ldfFile)
                    else:
                        print("您已放弃：未输入正常的数据和日志文件名。")
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 3:
                print("👉分数据库[1]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    self.detach()
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 4:
                print("👉备份数据库[2]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    fileFullName=input("2.备份文件名（绝对路径）：")
                    if fileFullName:
                        self.backup(fileFullName)
                    else:
                        print("您已放弃：未输入正确的备份文件名。")
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 5:
                print("👉备份所有数据库[1]：")
                self.database="master"
                fileFullName=input("1.备份路径（绝对路径）：")
                if fileFullName:
                    self.backupall(fileFullName)
                else:
                    print("您已放弃：未输入正确的备份文件名。")
                return True
            case 6:
                print("👉恢复数据库[2]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    fileFullName=input("2.备份文件名（绝对路径）：")
                    if fileFullName:
                        self.restore(fileFullName)
                    else:
                        print("您已放弃：未输入正确的备份文件名。")
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 7:
                print("👉删除日志[1]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    self.delLog()
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 8:
                print("👉清除NULL[1]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    self.clearNull()
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 9:
                print("👉执行SQL[2]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    sql=input("2.SQL语句：")
                    if sql:
                        self.runSQL(sql)
                    else:
                        print("您已放弃：未输入正确的SQL。")
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 10:
                print("👉执行SQL文件[3]：")
                self.database=input("1.数据库名称：")
                if self.database:
                    sql=input("2.SQL文件（绝对路径）：")
                    if sql:
                        useSQLCMD=input("3.是否用SQLCMD来执行（Y或N,默认N）：")
                        if not useSQLCMD:
                            useSQLCMD="N"
                        self.runSQLFile(sql,useSQLCMD.upper()=="N")
                    else:
                        print("您已放弃：未输入正确的SQL。")
                else:
                    print("您已放弃：未输入正确的数据库名称。")
                return True
            case 11:
                print("👉执行SSMS[0]：")
                self.openSSMS()
                return True
            case 0:
                return False
            case _:
                return True

    def choiceMenu(self):
        result = self.intputBase()
        if result:
            running = True
            while running:
                self.showMenu()
                try:
                    user_input = input("请输入您的选择（数字）: ")
                    choice = int(user_input)
                    running = self.choiceDo(choice)
                except ValueError:
                    print("\n>> 错误：输入无效，请输入数字！")
                    input(">> 按回车键继续...")

    def help(self):
        print("欢迎使用pylhb mssql命令")
        print("通用参数：")
        print("  -S/--server：服务器名称")
        print("  -P/--port：端口号")
        print("  -U/--user：用户名")
        print("  -P/--password：密码")
        print("  -D/--database：数据库")
        print("1.创建数据库")
        print("  A.mdf：数据文件")
        print("  B.ldf：日志文件")
        print("  如：pylhb mssql create -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf")
        print("2.附加数据库")
        print("  A.mdf：数据文件")
        print("  B.ldf：日志文件")
        print("  如：pylhb mssql attach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf")
        print("  如：pylhb mssql fujia -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf")
        print("3.分离数据库")
        print("  如：pylhb mssql detach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test")
        print("  如：pylhb mssql fenli -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test")
        print("4.备份数据库")
        print("  A.file：备份文件（绝对路径）")
        print("  如：pylhb mssql backup -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak")
        print("5.备份所有数据库")
        print("  A.file：备份文件（绝对路径），也可以是路径。")
        print("  如：pylhb mssql backupall -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak")
        print("6.恢复数据库")
        print("  A.file：备份文件（绝对路径）")
        print("  如：pylhb mssql restore -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak")
        print("7.删除日志")
        print("  如：pylhb mssql dellog -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer")
        print("8.清除null")
        print("  如：pylhb mssql clearnull -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer")
        print("9.删除数据库")
        print("  force：强制（必带）")
        print("  如：pylhb mssql drop -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test --force")
        print("10.执行SQL脚本")
        print("  A.sql：SQL脚本")
        print("  如：pylhb mssql runsql -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --sql “SELECT * FROM Dt_Users”")
        print("11.执行SQL文件")
        print("  A.file：SQL文件")
        print("  如：pylhb mssql runsqlfile -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\test.sql")
        print("12.打开SSMS")
        print("  如：pylhb mssql open")
        print("13.打开菜单操作模式")
        print("  如：pylhb mssql menu")
        
class IISDo:
    """IIS处理"""
    def createAppPool(self,poolName, runtimeVersion:str=None, enable32bit=False):
        """
        创建应用程序池
        Args：
            poolName：应用程序池名
            runtimeVersion：.NET CLR版本，如 "v4.0"，空字符串表示"无托管代码"
            enable32bit：是否启用32位应用程序
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在创建中...")
        sp.start()
        try:
            iis=MyIIS()
            exists=iis.checkAppPoolExists(poolName)
            if exists:
                sp.stop("已经存在。",False)
            else:
                iis.createAppPool(poolName,runtimeVersion)
                sp.stop("创建成功。")
        except Exception as e:
            sp.stop(f"创建失败：{e}",False)

    def deleteAppPool(self,poolName):
        """
        删除应用程序池
        Args：
            poolName：应用程序池名
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在删除中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.deleteAppPool(poolName)
            if successed:
                sp.stop("删除成功。")
            else:
                sp.stop(f"删除失败：{msg}")
        except Exception as e:
            sp.stop(f"删除失败：{e}",False)

    def createWebsite(self,siteName, physicalPath, port, hostName=None, poolName=None):
        """
        创建网站并绑定端口
        Args:
            siteName: 网站名称
            physicalPath: 网站文件的物理路径
            port: 绑定端口
            hostName: 绑定的域名（可选）
            poolName: 指定应用程序池（可选，不指定则使用默认池）
        Returns:
            是否成功
            执行结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在创建中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.createWebsite(siteName,physicalPath,port,hostName,poolName)
            if successed:
                sp.stop("创建成功。")
            else:
                sp.stop(f"创建失败：{msg}")
        except Exception as e:
            sp.stop(f"创建失败：{e}",False)

    def createWebsiteApp(self,siteName, appPath, physicalPath, poolName=None):
        """
        在网站下创建应用程序
        Args:
            siteName: 网站名称（如 "Default Web Site"）
            appPath: 应用程序路径（如 "/myapp" 或 "/api/v1"）
            physicalPath: 应用程序的物理路径
            poolName: 应用程序池名称（可选，不指定则继承父级）
        Returns:
            是否成功
            执行结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在创建中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.createWebsiteApplication(siteName,appPath,physicalPath,poolName)
            if successed:
                sp.stop("创建成功。")
            else:
                sp.stop(f"创建失败：{msg}")
        except Exception as e:
            sp.stop(f"创建失败：{e}",False)

    def deleteWebsite(self,siteName):
        """
        删除网站
        Args:
            siteName: 网站名称
        Returns:
            是否成功
            执行结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在删除中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.deleteWebsite(siteName)
            if successed:
                sp.stop("删除成功。")
            else:
                sp.stop(f"删除失败：{msg}")
        except Exception as e:
            sp.stop(f"删除失败：{e}",False)

    def deleteWebsiteApplication(self,siteName,appPath):
        """
        删除网站下的应用程序
        Args:
            siteName: 网站名称（如 "Default Web Site"）
            appPath: 应用程序路径（如 "/myapp" 或 "/api/v1"）
        Returns: 
            是否成功
            执行结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在删除中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.deleteWebsiteApplication(siteName,appPath)
            if successed:
                sp.stop("删除成功。")
            else:
                sp.stop(f"删除失败：{msg}")
        except Exception as e:
            sp.stop(f"删除失败：{e}",False)

    def checkAppPool(self,poolName):
        """
        检查应用程序池是否存在
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否存在
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在检测中...")
        sp.start()
        try:
            iis=MyIIS()
            successed=iis.checkAppPoolExists(poolName)
            if successed:
                sp.stop("存在。")
            else:
                sp.stop("不存在。",False)
        except Exception as e:
            sp.stop(f"检测失败：{e}",False)

    def checkWebsite(self,siteName):
        """
        检查网站是否存在
        Args:
            siteName: 网站名称
        Returns: 
            是否存在
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在检测中...")
        sp.start()
        try:
            iis=MyIIS()
            successed=iis.checkWebsiteExists(siteName)
            if successed:
                sp.stop("存在。")
            else:
                sp.stop("不存在。",False)
        except Exception as e:
            sp.stop(f"检测失败：{e}",False)

    def checkWebsiteApp(self,siteName,appPath):
        """
        检查网站应用程序是否存在
        Args:
            site_name: 网站名称
            app_path: 应用程序路径（如 "/app1"）
        Returns:
            是否存在
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在检测中...")
        sp.start()
        try:
            iis=MyIIS()
            successed=iis.checkWebsiteApplicationExists(siteName,appPath)
            if successed:
                sp.stop("存在。")
            else:
                sp.stop("不存在。",False)
        except Exception as e:
            sp.stop(f"检测失败：{e}",False)

    def startAppPool(self,poolName):
        """
        启动应用程序池
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在启动中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.startAppPool(poolName)
            if successed:
                sp.stop("启动成功。")
            else:
                sp.stop(f"启动失败：{msg}",False)
        except Exception as e:
            sp.stop(f"启动失败：{e}",False)

    def stopAppPool(self,poolName):
        """
        停止应用程序池
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在停止中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.stopAppPool(poolName)
            if successed:
                sp.stop("停止成功。")
            else:
                sp.stop(f"停止失败：{msg}",False)
        except Exception as e:
            sp.stop(f"停止失败：{e}",False)

    def startWebsite(self,siteName):
        """
        启用网站
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在启动中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.startWebsite(siteName)
            if successed:
                sp.stop("启动成功。")
            else:
                sp.stop(f"启动失败：{msg}",False)
        except Exception as e:
            sp.stop(f"启动失败：{e}",False)

    def stopWebsite(self,siteName):
        """
        停止网站
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在停止中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.stopWebsite(siteName)
            if successed:
                sp.stop("停止成功。")
            else:
                sp.stop(f"停止失败：{msg}",False)
        except Exception as e:
            sp.stop(f"停止失败：{e}",False)

    def getAppPoolState(self,poolName):
        """
        获取应用程序池状态
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在获取中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.getAppPoolState(poolName)
            if successed:
                sp.stop(f"状态：{msg}")
            else:
                sp.stop(f"获取失败：{msg}",False)
        except Exception as e:
            sp.stop(f"获取失败：{e}",False)

    def getWebsiteState(self,siteName):
        """
        获取网站状态
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在获取中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.getWebsiteState(siteName)
            if successed:
                sp.stop(f"状态：{msg}")
            else:
                sp.stop(f"获取失败：{msg}",False)
        except Exception as e:
            sp.stop(f"获取失败：{e}",False)

    def getAppPoolList(self):
        """
        获取应用程序池列表
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在获取中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.getAppPoolList()
            if successed:
                sp.stop("列表：")
                print(msg)
            else:
                sp.stop(f"获取失败：{msg}",False)
        except Exception as e:
            sp.stop(f"获取失败：{e}",False)

    def getWebsiteList(self):
        """
        获取网站列表
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在获取中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.getWebsiteList()
            if successed:
                sp.stop("列表：")
                print(msg)
            else:
                sp.stop(f"获取失败：{msg}",False)
        except Exception as e:
            sp.stop(f"获取失败：{e}",False)

    def backupIIS(self,backupName):
        """
        备份IIS
        Args：
            backupName：备份名
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在备份中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.backupIIS(backupName)
            if successed:
                sp.stop("备份成功。")
                print(r"备份路径：C:\Windows\System32\inetsrv\backup")
            else:
                sp.stop(f"备份失败：{msg}",False)
        except Exception as e:
            sp.stop(f"备份失败：{e}",False)

    def restoreIIS(self,backupName):
        """
        获取网站列表
        Returns: 
            是否成功
            结果
        """
        sp=MySpinner(SpinnerStyle.BRAILLE, "正在恢复中...")
        sp.start()
        try:
            iis=MyIIS()
            (successed,msg)=iis.restoreIIS(backupName)
            if successed:
                sp.stop("恢复成功。")
            else:
                sp.stop(f"恢复失败：{msg}",False)
        except Exception as e:
            sp.stop(f"恢复失败：{e}",False)

    def openIIS(self):
        """打开IIS管理器"""
        subprocess.Popen('start inetmgr', shell=True)

    def showMenu(self):
        print("\n" + "=" * 30)
        print("🌺🌺系统菜单")
        print("=" * 30)
        print("1.创建应用程序池")
        print("2.删除应用程序池")
        print("3.创建网站")
        print("4.创建网站应用程序")
        print("5.删除网站")
        print("6.删除网站应用程序")
        print("7.启动应用程序池")
        print("8.停止应用程序池")
        print("9.启用网站")
        print("10.停止网站")
        print("11.备份IIS")
        print("12.恢复IIS")
        print("13.打开IIS管理器")
        print("0.退出程序")
        print("=" * 30)
        
    def choiceDo(self,choice)->bool:
        match(choice):
            case 1:
                print("👉创建应用程序池[2]：")
                poolName=input("1.应用程序池名称：")
                if poolName:
                    runtimeVersion=input("2..NET CLR版本（空为无托管代码）：")
                    self.createAppPool(poolName,runtimeVersion)
                else:
                    print("您已放弃：未输入正确的应用程序池名称。")
                return True
            case 2:
                print("👉删除应用程序池[1]：")
                poolName=input("1.应用程序池名称：")
                if poolName:
                    self.deleteAppPool(poolName)
                else:
                    print("您已放弃：未输入正确的应用程序池名称。")
                return True
            case 3:
                print("👉创建网站[5]：")
                siteName=input("1.网站名称：")
                if siteName:
                    physicalPath=input("2.物理路径（绝对路径）：")
                    if physicalPath:
                        port=convertStr2Int(input("3.端口号："))
                        if port > 80:
                            hostNmae=input("4.域名（可选）：")
                            poolName=input("5.应用程序池名称（可选，空为默认池）：")
                            self.createWebsite(siteName,physicalPath,port,hostNmae,poolName)
                        else:
                            print("您已放弃：未输入正确的端口号。")
                    else:
                        print("您已放弃：未输入正确的物理路径。")
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 4:
                print("👉创建网站应用程序[4]：")
                siteName=input("1.网站名称：")
                if siteName:
                    appPath=input("2.应用程序名称（如/myapp）：")
                    if appPath:
                        physicalPath=input("3.物理路径（绝对路径）：")
                        if physicalPath:
                            poolName=input("4.应用程序池名称（可选，空为默认池）：")
                            self.createWebsiteApp(siteName,appPath,physicalPath,poolName)
                        else:
                            print("您已放弃：未输入正确的物理路径。")
                    else:
                        print("您已放弃：未输入正确的应用程序名称。")
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 5:
                print("👉删除网站[1]：")
                siteName=input("1.网站名称：")
                if siteName:
                    self.deleteWebsite(siteName)
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 6:
                print("👉删除网站应用程序[2]：")
                siteName=input("1.网站名称：")
                if siteName:
                    appPath=input("2.应用程序名称（如/myapp）：")
                    if appPath:
                        self.deleteWebsiteApplication(siteName,appPath)
                    else:
                        print("您已放弃：未输入正确的应用程序名称。")
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 7:
                print("👉启动应用程序池[1]：")
                poolName=input("1.应用程序池名称：")
                if poolName:
                    self.startAppPool(poolName)
                else:
                    print("您已放弃：未输入正确的应用程序池名称。")
                return True
            case 8:
                print("👉停止应用程序池[1]：")
                poolName=input("1.应用程序池名称：")
                if poolName:
                    self.stopAppPool(poolName)
                else:
                    print("您已放弃：未输入正确的应用程序池名称。")
                return True
            case 9:
                print("👉启动网站[1]：")
                siteName=input("1.网站名称：")
                if siteName:
                    self.startWebsite(siteName)
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 10:
                print("👉停止网站[1]：")
                siteName=input("1.网站名称：")
                if siteName:
                    self.stopWebsite(siteName)
                else:
                    print("您已放弃：未输入正确的网站名称。")
                return True
            case 11:
                print("👉备份IIS[1]：")
                backupName=input("1.备份名称：")
                if backupName:
                    self.backupIIS(backupName)
                else:
                    print("您已放弃：未输入正确的备份名称。")
                return True
            case 12:
                print("👉恢复IIS[1]：")
                print(r"注意：请先将路径复制到文件夹（C:\Windows\System32\inetsrv\backup）下。")
                backupName=input("1.备份名称：")
                if backupName:
                    self.restoreIIS(backupName)
                else:
                    print("您已放弃：未输入正确的备份名称。")
                return True
            case 13:
                print("👉打开IIS管理器[0]：")
                self.openIIS()
                return True
            case 0:
                return False
            case _:
                return True

    def choiceMenu(self):
        running = True
        while running:
            self.showMenu()
            try:
                user_input = input("请输入您的选择（数字）: ")
                choice = int(user_input)
                running = self.choiceDo(choice)
            except ValueError:
                print("\n>> 错误：输入无效，请输入数字！")
                input(">> 按回车键继续...")

    def help(self):
        print("欢迎使用pylhb iis命令")
        print("1.创建应用程序池")
        print("  A.poolname：应用程序池名称")
        print("  B.runtime：CTL版本（空表示无托管代码），默认为空。")
        print("  C.start32：是否启用32位应用程序，默认为False。")
        print("  如：pylhb iis createapppool --poolname MyPool")
        print("2.删除应用程序池")
        print("  A.poolname：应用程序池名称")
        print("  如：pylhb iis deleteapppool --poolname MyPool")
        print("3.创建网站")
        print("  A.sitename：网站名称")
        print("  B.physicalpath：物理路径")
        print("  C.port：端口号")
        print("  D.hostname：域名")
        print("  E.poolname：应用程序池")
        print("  如：pylhb iis createwebsite --sitename MyWebsite --path D:\\dd --port 88 --poolname MyPool")
        print("4.创建网站下的应用程序")
        print("  A.sitename：网站名称")
        print("  B.apppath：应用程序路径")
        print("  C.physicalpath：物理路径")
        print("  D.poolname：应用程序池")
        print("  如：pylhb iis createwebsiteapp --sitename MyWebsite --apppath /webapi --path D:\\dd --poolname MyPool")
        print("5.删除网站")
        print("  A.sitename：网站名称")
        print("  如：pylhb iis deletewebsite --sitename MyWebsite")
        print("6.删除网站下的应用程序")
        print("  A.sitename：网站名称")
        print("  b.apppath：应用程序路径")
        print("  如：pylhb iis deletewebsiteapp --sitename MyWebsite --apppath /webapi")
        print("7.检查应用程序池是否存在")
        print("  A.poolname：应用程序池名称")
        print("  如：pylhb iis checkapppool  --poolname MyPool")
        print("8.检查网站是否存在")
        print("  A.sitename：网站名称")
        print("  如：pylhb iis checkapppool  --sitename MyWebsite")
        print("9.检查网站下在应用是否存在")
        print("  A.sitename：网站名称")
        print("  b.apppath：应用程序路径")
        print("  如：pylhb iis checkwebsiteapp  --sitename MyWebsite --apppath /webapi")
        print("10.启动应用程序池")
        print("  A.poolname：应用程序池名称")
        print("  如：pylhb iis startapppool  --poolname MyPool")
        print("11.停止应用程序池")
        print("  A.poolname：应用程序池名称")
        print("  如：pylhb iis stopapppool  --poolname MyPool")
        print("12.启动网站")
        print("  A.sitename：网站名称")
        print("  如：pylhb iis startwebsite  --sitename MyWebsite")
        print("13.停止网站")
        print("  A.sitename：网站名称")
        print("  如：pylhb iis stopwebsite  --sitename MyWebsite")
        print("14.获取应用程序池状态")
        print("  A.poolname：应用程序池名称")
        print("  如：pylhb iis getapppoolstate  --poolname MyPool")
        print("15.获取网站状态")
        print("  A.sitename：网站名称")
        print("  如：pylhb iis getwebsitestate  --sitename MyWebsite")
        print("16.获取应用程序池列表")
        print("  如：pylhb iis getapppoollist")
        print("17.获取网站列表")
        print("  如：pylhb iis getwebsitelist")
        print("18.备份IIS")
        print("  A.backupname：备份名称")
        print("  如：pylhb iis backupiis --backupname bk2026")
        print("18.恢复IIS")
        print("  A.backupname：备份名称")
        print("  如：pylhb iis restoreiis --backupname bk2026")
        print(r"  注意：要把以前备份的复制到（C:\Windows\System32\inetsrv\backup）下")
        print("19.打开IIS管理器")
        print("  如：pylhb iis open")
        print("20.打开菜单操作模式")
        print("  如：pylhb iis menu")

class Dlowload:
    def __init__(self) -> None:
        pass

    def showMenu(self):
        print("\n" + "=" * 30)
        print("🌺🌺系统菜单🌺🌺")
        print("=" * 30)
        print("1. 微信")
        print("2. TIM")
        print("3. 微信web开发者工具")
        print("4. Node.js")
        print("5. Git")
        print("6. Zed")
        print("7. .Net")
        print("8. Python 3.12.9")
        print("9. Notepad3")
        print("10. DaVinci")
        print("88. 所有")
        print("0. 退出程序")
        print("=" * 30)
        
    def choiceMenu(self):
        running = True
        while running:
            self.showMenu()
            try:
                user_input = input("请输入您的选择（数字）: ")
                choice = int(user_input)
                running = self.choiceDo(choice)
            except ValueError:
                print("\n>> 错误：输入无效，请输入数字！")
                input(">> 按回车键继续...")
                
    def choiceDo(self,choice):
        match(choice):
            case 1:
                webbrowser.open("https://pc.qq.com/search.html#!keyword=%E5%BE%AE%E4%BF%A1")
                return True
            case 2:
                webbrowser.open("https://pc.qq.com/search.html#!keyword=TIM")
                return True
            case 3:
                webbrowser.open("https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html")
                return True
            case 4:
                webbrowser.open("https://nodejs.org/zh-cn")
                return True
            case 5:
                webbrowser.open("https://git-scm.com/install/windows")
                return True
            case 6:
                webbrowser.open("https://zed.dev/download")
                return True
            case 7:
                webbrowser.open("https://zed.dev/download")
                return True
            case 8:
                webbrowser.open("https://www.python.org/downloads/release/python-3129/")
                return True
            case 9:
                webbrowser.open("https://rizonesoft.com/downloads/notepad3/")
                return True
            case 10:
                webbrowser.open("http://www.blackmagicdesign.com/products/davinciresolve")
                return True
            case 88:
                # 微信
                webbrowser.open("https://pc.qq.com/search.html#!keyword=%E5%BE%AE%E4%BF%A1")
                # TIM
                webbrowser.open("https://pc.qq.com/search.html#!keyword=TIM")
                # 微信web开发者工具
                webbrowser.open("https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html")
                # Node.js
                webbrowser.open("https://nodejs.org/zh-cn")
                # Git
                webbrowser.open("https://git-scm.com/install/windows")
                # Zed
                webbrowser.open("https://zed.dev/download")
                # .Net
                webbrowser.open("https://dotnet.microsoft.com/zh-cn/download")
                # Python 3.12.9
                webbrowser.open("https://www.python.org/downloads/release/python-3129/")
                # Notepad3
                webbrowser.open("https://rizonesoft.com/downloads/notepad3/")
                # DaVinci
                webbrowser.open("http://www.blackmagicdesign.com/products/davinciresolve")
                return True
            case 0:
                return False
            case _:
                return True

    def help(self):
        print("欢迎使用pylhb download命令")
        print("1.打开菜单操作模式")
        print("  如：pylhb download menu")