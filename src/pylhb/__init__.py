import argparse
import platform
# Base
from .lhb import showVersion,showDeviceInfos,MyMSSQLDo,IISDo
# Mr.Lee's Module
from .myini import MyINI
from .myjson import MyJSON
from .mylog import MyLog
from .mymssql import MyMSSQL
from .mymssqlmanager import MyMSSQLManager
from .mysqlite import MySQLite
from .mycipher import MyAsymClipher,MyXORCipher,MyFernetCipher,MyBlowfishCipher
from .mysnowflake import MySnowflake
from .mydevice import MyDevice
from .myemail import MyEmail
from .myfile import MyFile
from .mydownload import MyDownload
from .mydatetime import MyDateTime
from .mysqlinjection import MySQLInjection
from .mycodeadd import MyCodeAdd
from .mycron import MyCron
from .myre import MyRe
from .myspinner import SpinnerStyle,MySpinner

# 导出列表
__all__ = []
if platform.system()=="Windows":
    from .mysubscribe import MySubscribe
    from .myiis import MyIIS
    from .myreg import MyReg
    from .myenv import MyEnv
    __all__.extend(["MySubscribe", "MyIIS", "MyReg","MyEnv"])
if platform.system()=="Linux":
    from .mysubscribe import MySubscribe
    __all__.extend(["MySubscribe",])

# 跨平台通用接口
__all__.append([
    "MyINI",
    "MyJSON",
    "MyLog",
    "MyMSSQL",
    "MyMSSQLManager",
    "MySQLite",
    "MyAsymClipher",
    "MyXORCipher",
    "MyFernetCipher",
    "MyBlowfishCipher",
    "MySnowflake",
    "MyDevice",
    "MySubscribe",
    "MyIIS",
    "MyReg",
    "MyEmail",
    "MyFile",
    "MyDownload",
    "MyDateTime",
    "MySQLInjection",
    "MyCodeAdd",
    "MyCron",
    "MyRe",
    "SpinnerStyle",
    "MySpinner"
])

def main() -> None:
    parser = argparse.ArgumentParser(description="Mr.Lee's Helpers")
    # 位置参数
    parser.add_argument("commands", nargs="?", default=None, choices=["mssql", "iis"], help="Commands")
    parser.add_argument("subcommands", nargs="?", default=None, choices=["create","attach","fujia","detach","fenli","backup","backupall","restore", 
        "dellog","clearnull","drop","runsql","runsqlfile","createapppool","deleteapppool","createwebsite","createwebsiteapp",
        "deletewebsite","deletewebsiteapp","checkapppool","checkwebsite","checkwebsiteapp","startapppool","stopapppool","startwebsite",
        "stopwebsite","getapppoolstate","getwebsitestate","getapppoollist","getwebsitelist","backupiis","restoreiis","open",
        "choice","menu"], help="Subcommands")
    # 常规参数
    parser.add_argument('-v', '--version', action='store_true', help='显示版本号')
    parser.add_argument('-d', '--deviceinfos', action='store_true', help='显示设备信息')
    # mssql参数
    parser.add_argument("-S", "--server", default="127.0.0.1", type=str, help="服务器名称，默认127.0.0.1")
    parser.add_argument("-PT", "--port", default=1433, type=int, help="端口号，默认1433")
    parser.add_argument("-U", "--user", default="sa", type=str, help="用户，默认sa")
    parser.add_argument("-P", "--password", default="", type=str, help="密码")
    parser.add_argument("-D", "--database", default="master", type=str, help="数据库")
    parser.add_argument("--file", default="", type=str, help="文件名（绝对路径）")
    parser.add_argument("-mdf", "--mdffile", default="", type=str, help="数据文件")
    parser.add_argument("-ldf", "--ldffile", default="", type=str, help="日志文件")
    parser.add_argument("--force", action='store_true', help='强制，删除数据库必须带上')
    parser.add_argument("--trusted", action='store_true', help='信任（Windows身份登录)')
    # IIS参数
    parser.add_argument("--poolname", default="", type=str, help="应用程序池名")
    parser.add_argument("--runtime", default="", type=str, help=".NET CLR版本，如'v4.0'，空字符串表示'无托管代码'")
    parser.add_argument("--start32", action='store_true', help='是否启用32位应用程序')
    parser.add_argument("--sitename", default="", type=str, help="网站名称")
    parser.add_argument("--apppath", default="", type=str, help="应用程序路径（如 '/myapp' 或 '/api/v1'）")
    parser.add_argument("--path", default="", type=str, help="网站文件的物理路径")
    parser.add_argument("--hostname", default="", type=str, help="绑定的域名（可选）")
    parser.add_argument("--backupname", default="", type=str, help="备份名称")
    parser.add_argument("--usesqlcmd", action='store_true', help='用SQLCMD执行SQL')
    parser.add_argument("--sql", default="", type=str, help="SQL脚本")
    # 解析
    args = parser.parse_args()

    if args.commands:
        match args.commands:
            case "mssql":
                mssql=MyMSSQLDo(args.server,args.port,args.user,args.password,args.database,args.trusted)
                match args.subcommands:
                    case "create":
                        # 创建数据库
                        # pylhb mssql create -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
                        mssql.create(args.mdffile,args.ldffile)
                    case "attach" | "fujia":
                        # 附加数据库
                        # pylhb mssql attach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
                        # pylhb mssql fujia -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
                        mssql.attach(args.mdffile,args.ldffile)
                    case "detach" | "fenli":
                        # 分离数据库
                        # pylhb mssql detach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test
                        # pylhb mssql fenli -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test
                        mssql.detach()
                    case "backup":
                        # 备份数据库
                        # pylhb mssql backup -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak
                        mssql.backup(args.file)
                    case "backupall":
                        # 备份所有数据库
                        # pylhb mssql backupall -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\name.bak
                        mssql.backupall(args.file)
                    case "restore":
                        # 恢复数据库
                        # pylhb mssql restore -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak
                        mssql.restore(args.file)
                    case "dellog":
                        # 清除日志
                        # pylhb mssql dellog -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer
                        mssql.delLog()
                    case "clearnull":
                        # 清除null
                        # pylhb mssql clearnull -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer
                        mssql.clearNull()
                    case "drop":
                        # 删除数据库
                        # pylhb mssql drop -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test --force
                        if args.force:
                            mssql.drop()
                        else:
                            print("删除数据库必须带force参数")
                    case "runsql":
                        # 执行SQL脚本
                        # pylhb mssql runsql -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --sql “SELECT * FROM Dt_Users”
                        mssql.runSQL(args.sql)
                    case "runsqlfile":
                        # 执行SQL文件
                        # pylhb mssql runsqlfile -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\test.sql
                        mssql.runSQLFile(args.file,args.usesqlcmd)
                    case "open":
                        # 打开SSMS
                        # pylhb mssql open
                        mssql.openSSMS()
                    case "choice" | "menu":
                        # 打开菜单选择操作
                        # pylhb mssql choice
                        mssql.choiceMenu()
            case "iis":
                iis=IISDo()
                match args.subcommands:
                    case "createapppool":
                        # 创建应用程序池
                        # pylhb iis createapppool --poolname MyPool
                        # pylhb iis createapppool --poolname MyPool --runtime v4.0 --start32
                        iis.createAppPool(args.poolname,args.runtime,args.start32)
                    case "deleteapppool":
                        # 删除应用程序池
                        # pylhb iis deleteapppool --poolname MyPool
                        iis.deleteAppPool(args.poolname)
                    case "createwebsite":
                        # 创建网站
                        # pylhb iis createwebsite --sitename MyWebsite --path D:\\dd --port 88 --poolname MyPool
                        iis.createWebsite(args.sitename,args.path,args.port,args.hostname,args.poolname)
                    case "createwebsiteapp":
                        # 创建网站下的应用
                        # pylhb iis createwebsiteapp --sitename MyWebsite --apppath /webapi --path D:\\dd --poolname MyPool
                        iis.createWebsiteApp(args.sitename,args.apppath,args.path,args.poolname)
                    case "deletewebsite":
                        # 删除网站
                        # pylhb iis deletewebsite --sitename MyWebsite
                        iis.deleteWebsite(args.sitename)
                        pass
                    case "deletewebsiteapp":
                        # 删除网站应用
                        # pylhb iis deletewebsiteapp --sitename MyWebsite --apppath /webapi
                        iis.deleteWebsiteApplication(args.sitename,args.apppath)
                    case "checkapppool":
                        # 检查应用程序池是否存在
                        # pylhb iis checkapppool  --poolname MyPool
                        iis.checkAppPool(args.poolname)
                    case "checkwebsite":
                        # 检查网站是否存在
                        # pylhb iis checkwebsite  --sitename MyWebsite
                        iis.checkWebsite(args.sitename)
                    case "checkwebsiteapp":
                        # 检查网站下在应用是否存在
                        # pylhb iis checkwebsiteapp  --sitename MyWebsite --apppath /webapi
                        iis.checkWebsiteApp(args.sitename,args.apppath)
                    case "startapppool":
                        # 启动应用程序池
                        # pylhb iis startapppool  --poolname MyPool
                        iis.startAppPool(args.poolname)
                    case "stopapppool":
                        # 停止应用程序池
                        # pylhb iis stopapppool  --poolname MyPool
                        iis.stopAppPool(args.poolname)
                    case "startwebsite":
                        # 启动网站
                        # pylhb iis startwebsite  --sitename MyWebsite
                        iis.startWebsite(args.sitename)
                    case "stopwebsite":
                        # 停止网站
                        # pylhb iis stopwebsite  --sitename MyWebsite
                        iis.stopWebsite(args.sitename)
                    case "getapppoolstate":
                        # 获取应用程序池状态
                        # pylhb iis getapppoolstate  --poolname MyPool
                        iis.getAppPoolState(args.poolname)
                    case "getwebsitestate":
                        # 获取网站状态
                        # pylhb iis getwebsitestate  --sitename MyWebsite
                        iis.getWebsiteState(args.sitename)
                    case "getapppoollist":
                        # 获取应用程序池列表
                        # pylhb iis getapppoollist
                        iis.getAppPoolList()
                    case "getwebsitelist":
                        # 获取网站列表
                        # pylhb iis getwebsitelist
                        iis.getWebsiteList()
                    case "backupiis":
                        # 备份IIS
                        # pylhb iis backupiis --backupname bk2026
                        # 备份成功后在文件夹（C:\Windows\System32\inetsrv\backup）下就有一个bk2026的文件夹。
                        iis.backupIIS(args.backupname)
                    case "restoreiis":
                        # 恢复IIS
                        # pylhb iis restoreiis --backupname bk2026
                        # 恢复时，要把以前备份的文件夹bk2026复制到（C:\Windows\System32\inetsrv\backup）下。
                        iis.restoreIIS(args.backupname)
                    case "open":
                        # 打开IIS管理器
                        # pylhb iis open
                        iis.openIIS()
                    case "choice" | "menu":
                        # 打开菜单选择操作
                        # pylhb iis choice
                        iis.choiceMenu()
    else:
        # show version
        if args.version:
            showVersion()
            return
            
        # show device infomations
        if args.deviceinfos:
            showDeviceInfos()
            return

if __name__ == '__main__':
    main()