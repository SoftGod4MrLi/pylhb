from nt import truncate
import os
import platform
from datetime import datetime
from .mymssqlmanager import MyMSSQLManager
from .mydevice import MyDevice
from .myspinner import SpinnerStyle,MySpinner
from .mymssql import MyMSSQL
from .myiis import MyIIS
import subprocess

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
    def __init__(self, server,port, user, password, database,trusted=False):
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
        启动应用程序池
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
        停止应用程序池
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