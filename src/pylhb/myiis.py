"""
模块：myiis
作者：李生
描述：IIS应用程序池、网站、应用管理
"""
import subprocess

class MyIIS:
    """
    IIS管理类
    """
    def runAppCMD(self,command) -> tuple[bool,str]:
        """
        执行appcmd命令并打印结果
        Args:
            command：命令
        Returns:
            是否成功
            执行结果
        """
        appcmdPath = r"%windir%\system32\inetsrv\appcmd.exe"
        fullCommand = f"{appcmdPath} {command}"
        try:
            # 执行命令
            result = subprocess.run(fullCommand, shell=True, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                if result.stdout:
                    return result.returncode == 0,f"{result.stdout.strip()}"
                else:
                    return result.returncode == 0,"OK"
            else:
                return False,f"{result.stderr.strip() if result.stderr else result.stdout.strip()}"
        except Exception as e:
            return False,f"{e}"
            
    def checkAppPoolExists(self,poolName) -> bool:
        """
        检查应用程序池是否存在
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否存在
        """
        # 使用list命令加精确名称查询，/xml参数让输出更易解析
        succesed,result = self.runAppCMD(f'list apppool /name:"{poolName}"')
        if succesed:
            # 如果找到，输出中会包含该应用池的信息
            return poolName.lower() in result.lower()
        return False

    # 创建应用程序池
    def createAppPool(self,poolName, runtimeVersion:str=None, enable32bit=False) -> tuple[bool,str]:
        """
        创建应用程序池
        Args:
            poolName: 应用程序池名称
            runtimeVersion: .NET CLR版本，如 "v4.0"，空字符串表示"无托管代码"
            enable32bit: 是否启用32位应用程序
        Returns:
            是否成功
            执行结果
        """
        # 构建命令参数
        command = f'add apppool /name:"{poolName}"'
        # 设置.NET CLR版本
        if runtimeVersion:
            command += f' /managedRuntimeVersion:"{runtimeVersion}"'
        else:
            command += ' /managedRuntimeVersion:""'
        # 设置是否启用32位应用程序
        if enable32bit:
            command += ' /enable32BitAppOnWin64:"True"'
        return self.runAppCMD(command)
        
    def deleteAppPool(self,poolName) -> tuple[bool,str]:
        """
        删除应用程序池
        Args:
            poolName: 应用程序池名称
        Returns:
            是否成功
            执行结果
        """
        # 检查应用程序池是否存在
        if not self.checkAppPoolExists(poolName):
            return False,"应用程序池不存在。"
        # 停止应用程序池（强制删除时先停止）
        self.runAppCMD(f'stop apppool "{poolName}"')
        # 删除应用程序池
        successed,result = self.runAppCMD(f'delete apppool "{poolName}"')
        if successed:
            return True,"OK"
        else:
            return False,result
    
    def checkWebsiteExists(self,siteName) -> bool:
        """
        检查网站是否存在
        Args:
            siteName: 网站名称
        Returns: 
            是否存在
        """
        successed,result = self.runAppCMD(f'list site /name:"{siteName}"')
        if successed:
            return siteName.lower() in result.lower()
        return False
        
    def checkWebsiteApplicationExists(self,siteName, appPath) -> bool:
        """
        检查应用程序是否存在
        Args:
            site_name: 网站名称
            app_path: 应用程序路径（如 "/app1"）
        Returns:
            是否存在
        """
        successed,result = self.runAppCMD(f'list app /site.name:"{siteName}" /path:"{appPath}"')
        return successed
        
    def createWebsite(self,siteName, physicalPath, port, hostName=None, poolName=None) -> tuple[bool,str]:
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
        # 构建绑定信息
        bindingInfo = f":{port}:"
        if hostName:
            bindingInfo = f":{port}:{hostName}"
        # 构建命令参数
        command = f'add site /name:"{siteName}" /physicalPath:"{physicalPath}" /bindings:"http/{bindingInfo}"'
        # 执行创建网站命令
        successed,result=self.runAppCMD(command)
        if not successed:
            return False,result
        # 如果指定了应用程序池，则修改网站使用的应用程序池
        if poolName:
            command = f'set site /site.name:"{siteName}" /applicationDefaults.applicationPool:"{poolName}"'
            successed,result = self.runAppCMD(command)
            return successed,result
        return True,"OK"
        
    def createWebsiteApplication(self,siteName, appPath, physicalPath, poolName=None) -> tuple[bool,str]:
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
        # 检查网站是否存在
        if not self.checkWebsiteExists(siteName):
            return False,"网站不存在。"
        # 检查应用程序是否已存在
        if self.checkWebsiteApplicationExists(siteName, appPath):
            return False,"应用程序已存在。"
        # 构建创建命令
        command = f'add app /site.name:"{siteName}" /path:"{appPath}" /physicalPath:"{physicalPath}"'
        # 如果指定了应用程序池，添加到命令中
        if poolName:
            if not self.checkAppPoolExists(poolName):
                return False,"应用程序池不存在。"
            command += f' /applicationPool:"{poolName}"'
        # 执行创建
        successed,result = self.runAppCMD(command)
        return successed,result
        
    def deleteWebsite(self, siteName) -> tuple[bool,str]:
        """
        删除网站
        Args:
            siteName: 网站名称
        Returns:
            是否成功
            执行结果
        """
        # 检查网站是否存在
        if not self.checkWebsiteExists(siteName):
            return False,"网站不存在。"
        # 停止网站（删除前先停止）
        self.runAppCMD(f'stop site "{siteName}"')
        # 删除网站
        successed,result = self.runAppCMD(f'delete site "{siteName}"')
        if successed:
            return True,"OK"
        return successed,result
        
    def deleteWebsiteApplication(self,siteName, appPath) -> tuple[bool,str]:
        """
        删除网站下的应用程序
        Args:
            siteName: 网站名称（如 "Default Web Site"）
            appPath: 应用程序路径（如 "/myapp" 或 "/api/v1"）
        Returns: 
            是否成功
            执行结果
        """
        # 检查网站是否存在
        if not self.checkWebsiteExists(siteName):
            return False,"网站不存在。"
        # 检查应用程序是否存在
        if not self.checkWebsiteApplicationExists(siteName, appPath):
            return False,"应用程序不存在。"
        # 停止网站（删除前先停止）
        self.runAppCMD(f'stop site "{siteName}"')
        # 删除应用程序
        successed,result = self.runAppCMD(f'delete app "{siteName}{appPath}"')
        if successed:
            return True,"OK"
        else:
            return False,result

    def startAppPool(self,poolName)  -> tuple[bool,str]:
        """
        启动应用程序池
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'start apppool "{poolName}"')
        return succesed,result

    def stopAppPool(self,poolName)  -> tuple[bool,str]:
        """
        停止应用程序池
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'stop apppool "{poolName}"')
        return succesed,result

    def startWebsite(self,siteName)  -> tuple[bool,str]:
        """
        启动网站
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'start site "{siteName}"')
        return succesed,result

    def stopWebsite(self,siteName)  -> tuple[bool,str]:
        """
        停止网站
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'stop site "{siteName}"')
        return succesed,result

    def getAppPoolState(self,poolName)  -> tuple[bool,str]:
        """
        获取应用程序池状态
        Args:
            poolName: 应用程序池名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'list apppool "{poolName}" /text:state')
        return succesed,result

    def getWebsiteState(self,siteName)  -> tuple[bool,str]:
        """
        获取网站状态
        Args:
            siteName: 网站名称
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'list site "{siteName}" /text:state')
        return succesed,result

    def getAppPoolList(self)  -> tuple[bool,str]:
        """
        获取应用程序池列表
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'list apppool')
        return succesed,result

    def getWebsiteList(self)  -> tuple[bool,str]:
        """
        获取网站列表
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'list site')
        return succesed,result

    def backupIIS(self,backupName)  -> tuple[bool,str]:
        """
        备份IIS
        Args：
            backupName：备份名
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'add backup {backupName}')
        return succesed,result

    def restoreIIS(self,backupName)  -> tuple[bool,str]:
        """
        恢复IIS
        Args：
            backupName：备份名
        Returns: 
            是否成功
            结果
        """
        succesed,result = self.runAppCMD(f'restore backup {backupName}')
        return succesed,result