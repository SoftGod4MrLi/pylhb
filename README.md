# pylhb

[![PyPI version](https://img.shields.io/pypi/v/pylhb.svg)](https://pypi.org/project/pylhb/)
[![GitHub stars](https://img.shields.io/github/stars/SoftGod4MrLi/pylhb?style=flat&logo=github)](https://github.com/SoftGod4MrLi/pylhb)
[![GitHub license](https://img.shields.io/github/license/SoftGod4MrLi/pylhb?style=flat)](https://github.com/SoftGod4MrLi/pylhb/blob/main/LICENSE)
![GitHub repo size](https://img.shields.io/github/repo-size/SoftGod4MrLi/pylhb?style=flat)
[![GitHub forks](https://img.shields.io/github/forks/SoftGod4MrLi/pylhb?style=flat&logo=github)](https://github.com/SoftGod4MrLi/pylhb)

pylhb 是我在工作过程中陆续整理的一个 Python 工具包，里面放了一些自己反复用到的模块和函数。与其说是一个正式的开源项目，不如说是我自己的“代码杂物间”——只不过把它打包了一下，方便在不同项目之间复用。
> 由于是个人使用为主，很多设计可能带着比较强的个人习惯，也未必是最优解。如果您发现了问题或有更好的建议，非常欢迎指正。

## 安装
```
pip install pylhb
```

## 🌺命令
### Microsoft SQL Server命令：
- 创建数据库
```
pylhb mssql create -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
```
- 附加数据库
```
pylhb mssql attach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
pylhb mssql fujia -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test -mdf D:\\dd\\test.mdf -ldf D:\\dd\\test_log.ldf
```
- 分离数据库
```
pylhb mssql detach -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test
pylhb mssql fenli -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test
```
- 备份数据库
```
pylhb mssql backup -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak
```
- 备份所有数据库
```
pylhb mssql backupall -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\name.bak
```
- 恢复数据库
```
pylhb mssql restore -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\bkfile.bak
```
- 清除日志
```
pylhb mssql dellog -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer
```
- 清除null
```
pylhb mssql clearnull -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer
```
- 删除数据库
```
pylhb mssql drop -S localhost\\sqlexpress -U sa -P fpsoft@123 -D test --force
```
- 执行SQL脚本
```
pylhb mssql runsql -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --sql “SELECT * FROM Dt_Users”
```
- 执行SQL文件
```
pylhb mssql runsqlfile -S localhost\\sqlexpress -U sa -P fpsoft@123 -D MyCustomer --file D:\\dd\\test.sql
```
- 打开SSMS
```
pylhb mssql open
```
### IIS命令：
- 创建应用程序池
```
pylhb iis createapppool --poolname MyPool
pylhb iis createapppool --poolname MyPool --runtime v4.0 --start32
```
- 删除应用程序池
```
pylhb iis deleteapppool --poolname MyPool
```
- 创建网站
```
pylhb iis createwebsite --sitename MyWebsite --path D:\\dd --port 88 --poolname MyPool
```
- 创建网站下的应用
```
pylhb iis createwebsiteapp --sitename MyWebsite --apppath /webapi --path D:\\dd --poolname MyPool
```
- 删除网站
```
pylhb iis deletewebsite --sitename MyWebsite
```
- 删除网站应用
```
pylhb iis deletewebsiteapp --sitename MyWebsite --apppath /webapi
```
- 检查应用程序池是否存在
```
pylhb iis checkapppool  --poolname MyPool
```
- 检查网站是否存在
```
pylhb iis checkwebsite  --sitename MyWebsite
```
- 检查网站下在应用是否存在
```
pylhb iis checkwebsiteapp  --sitename MyWebsite --apppath /webapi
```
- 启动应用程序池
```
pylhb iis startapppool  --poolname MyPool
```
- 停止应用程序池
```
pylhb iis stopapppool  --poolname MyPool
```
- 启动网站
```
pylhb iis startwebsite  --sitename MyWebsite
```
- 停止网站
```
pylhb iis stopwebsite  --sitename MyWebsite
```
- 获取应用程序池状态
```
pylhb iis getapppoolstate  --poolname MyPool
```
- 获取网站状态
```
pylhb iis getwebsitestate  --sitename MyWebsite
```
- 获取应用程序池列表
```
pylhb iis getapppoollist
```
- 获取网站列表
```
pylhb iis getwebsitelist
```
- 备份IIS
```
pylhb iis backupiis --backupname bk2026
```
- 恢复IIS
```
pylhb iis restoreiis --backupname bk2026
```
- 打开IIS管理器
```
pylhb iis open
```

## 🌺mymssql模块

通过ODBC访问Microsoft SQL Server。

注意：

> ODBC Driver 17 for SQL Server下载：  
> https://learn.microsoft.com/zh-cn/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver16  
> 注意，如果是ODBC Driver 18 for SQL Server，那实例化时记得传driver.

使用示例：

```
from pylhb.mymssql import MyMSSQL

if __name__ == "__main__":
    server="127.0.0.1"
    user="sa"
    password="fpsoft@123"
    database="MyCustomer"
    # 实例化
    #mssql=MyMSSQL(server=server,database=database)
    mssql=MyMSSQL(server=server,user=user,password=password,database=database)
    # 连接数据库
    (successed,msg)=mssql.connect()
    # print(successed)
    # print(msg)

    # Demo1：查询数据
    sql="SELECT TOP 2 P_CusName,P_Tel FROM Dt_Customers WITH(NOLOCK)"
    print("🌸Demot1：获取客户：")
    humans=mssql.get(sql)
    print(humans)

    # Demo2：执行无参存储过程
    # (successed,msg) = mssql.execProc("Usp_TestNoArgs")
    # print("🌸Demot2：执行无参存储过程(Usp_TestNoArgs)：")
    # print(successed,msg)

    # Demo3：执行带参存储过程
    # (successed,msg) = mssql.execProc("Usp_TestWithArgs",(99,"1号机"))
    # print("🌸Demot3：执行带参存储过程(Usp_TestWithArgs)：")
    # print(successed,msg)

    # Demo4：执行存储过程并返回数据
    # (successed,msg,datas) = mssql.execProcGet("Usp_Test",("",))
    # print("🌸Demot4：执行存储过程并返回数据(Usp_Test)：")
    # print(successed,msg,datas)

    # Demo5：Insert
    # user1 = {"P_UserName": "张三", "P_Age": 25, "P_Email": "Zhang3@example.com"}
    # user2 = {"P_UserName": "李四", "P_Age": 20, "P_Email": "Li4@example.com"}
    # user3 = {"P_UserName": "王五", "P_Age": 18, "P_Email": "Wang5@example.com"}
    # (successed,msg)=mssql.insert("Dt_User",user1)
    # (successed,msg)=mssql.insert("Dt_User",user2)
    # (successed,msg)=mssql.insert("Dt_User",user3)
    # print(successed,msg)

    # Demo6：Update
    # updateData = {"P_Age": 31,"P_Email":"Zhang3@QQ.com"}
    # (successed,msg)=mssql.update("Dt_User", updateData, "P_UserName = ?",('张三',))
    # print(successed,msg)

    # Demo7：Delete
    # (successed,msg)=mssql.delete("Dt_User", "P_UserName = ?", ("王五",))
    # print(successed,msg)

    # Demo8：Select
    # cols=("P_UserName","P_Age")
    # cols=None
    # (successed,msg,data)=mssql.select("Dt_User",cols,"P_UserName = ?",("张三",))
    # print(successed,msg,data)

    # 提交事务
    mssql.commit()
    # 关闭
    mssql.close()
```

## 🌺myconfig模块

通过configparser读取配置文件。

使用示例：

```
from pylhb.myconfig import MyConfig

if __name__ == "__main__":
    config = MyConfig("config.ini")
    config.set("main", "host", "127.0.0.1")
    print(config.get("main", "host"))
```

## 🌺mysqlite模块

通过sqlite3访问SQLite数据库。

使用示例：

```
from pylhb.mysqlite import MySQLite
if __name__ == "__main__":
    # 创建数据库实例
    db = MySQLite("test.db")

    # 连接数据库
    db.connect()

    # 创建表
    columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "age": "INTEGER",
        "email": "TEXT"
    }
    db.createTable("users", columns)

    # 插入数据
    user1 = {"name": "张三", "age": 25, "email": "zhangsan@example.com"}
    user2 = {"name": "李四", "age": 30, "email": "lisi@example.com"}
    user3 = {"name": "王五", "age": 28, "email": "wangwu@example.com"}

    db.insert("users", user1)
    db.insert("users", user2)
    db.insert("users", user3)

    # 查询所有数据
    print("所有用户:")
    users = db.select("users")
    for user in users:
        print(user)

    # 条件查询
    print("\n年龄大于28的用户:")
    users = db.select("users", where="age > ?", params=(28,))
    for user in users:
        print(user)

    # 更新数据
    update_data = {"age": 31}
    db.update("users", update_data, "name = ?", ("李四",))

    # 查询特定列
    print("\n用户姓名和邮箱:")
    users = db.select("users", columns=["name", "email"])
    for user in users:
        print(user)

    # 删除数据
    db.delete("users", "name = ?", ("王五",))

    # 再次查询所有数据
    print("\n删除后的所有用户:")
    users = db.select("users")
    for user in users:
        print(user)

    # 关闭连接
    db.close()
```

## 🌺mylog模块

本地日志操作。

使用示例：

```
from pylhb.mylog import MyLog

if __name__ == "__main__":
    myLog= MyLog()
    myLog.add("This is a test log entry.")
```

## 🌺myjson模块

json配置操作

使用示例：

```
from pylhb.myjson import MyJSON

if __name__ == "__main__":
    appJson = MyJSON("config.json")
    print(appJson.get("host"))
```

## 🌺mysqlite模块

SQLite操作

使用示例：

```
from pylhb.mysqlite import SQLite

if __name__ == "__main__":
    # 创建数据库实例
    db = SQLite("test.db")

    # 连接数据库
    db.connect()

    # 创建表
    columns = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "age": "INTEGER",
        "email": "TEXT"
    }
    db.createTable("users", columns)

    # 插入数据
    user1 = {"name": "张三", "age": 25, "email": "zhangsan@example.com"}
    user2 = {"name": "李四", "age": 30, "email": "lisi@example.com"}
    user3 = {"name": "王五", "age": 28, "email": "wangwu@example.com"}

    db.insert("users", user1)
    db.insert("users", user2)
    db.insert("users", user3)

    # 查询所有数据
    print("所有用户:")
    users = db.select("users")
    for user in users:
        print(user)

    # 条件查询
    print("\n年龄大于28的用户:")
    users = db.select("users", where="age > ?", params=(28,))
    for user in users:
        print(user)

    # 更新数据
    update_data = {"age": 31}
    db.update("users", update_data, "name = ?", ("李四",))

    # 查询特定列
    print("\n用户姓名和邮箱:")
    users = db.select("users", columns=["name", "email"])
    for user in users:
        print(user)

    # 删除数据
    db.delete("users", "name = ?", ("王五",))

    # 再次查询所有数据
    print("\n删除后的所有用户:")
    users = db.select("users")
    for user in users:
        print(user)

    # 关闭连接
    db.close()
```

## 🌺mycipher模块

加解密

使用示例：

```
from pylhb.mycipher import MyAsymClipher,MyXORCipher,MyFernetCipher,MyBlowfishCipher

if __name__ == "__main__":
  # 非对称加密
  ac=MyAsymClipher()
  print(ac.md5("Mr.Lee"))
  print(ac.sha256("Mr.Lee"))
  # XOR对称加解密
  xor=MyXORCipher(key)
  xor.encrypt("") # 加密
  xor.decrypt("") # 解密
  # Fernet对称加解密
  ft=MyFernetCipher(key)
  ft.encrypt("") # 加密
  ft.decrypt("") # 解密
  # Blowfish对称加解密
  bf=MyBlowfishCipher(key)
  bf.encrypt("") # 加密
  bf.decrypt("") # 解密
```

## 🌺mysnowflake模块

雪花ID

使用示例：

```
from pylhb.mysnowflake import MySnowflake

if __name__ == "__main__":
    workerID = 1 # 机器ID
    datacenterID = 1 # 数据中心ID
    snowflake = MySnowflake(workerID, datacenterID)
    # 生成10个ID
    for _ in range(10):
        print(snowflake.generateID())
```

## 🌺mydevice模块

设备管理

使用示例：

```
from pylhb.mydevice import MyDevice

if __name__ == "__main__":
  d=MyDevice()
  print(d.getHostName())
  print(d.getDeviceID())
  print(d.getMAC())
  print(d.getLocalIP())
```

## 🌺myspinner模块

进度条

使用示例：

```
import time
from pylhb.myspinner import SpinnerStyle,MySpinner

if __name__ == "__main__":
    # 盲文风格（最漂亮）
    spinner = MySpinner(SpinnerStyle.BRAILLE, "初始化任务...")
    spinner.start()
    time.sleep(1.5)
    spinner.setText("正在下载资源...")
    time.sleep(2)
    spinner.setText("解析数据中...")
    time.sleep(2)
    spinner.setText("生成结果...")
    time.sleep(1.5)
    spinner.stop("任务全部成功完成！")

    # 中断测试
    spinner2 = MySpinner(SpinnerStyle.CLASSIC, "准备测试...")
    spinner2.start()
    time.sleep(1)
    spinner2.setText("即将中断...")
    time.sleep(1)
    spinner2.stop("手动终止成功",showIcon=False)
```
