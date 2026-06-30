"""
模块：myenv
作者：李生
描述：Windows环境变量管理
"""
import os
import winreg
import ctypes
from typing import List, Dict, Optional, Union

class MyEnv:
    """
    Windows环境变量管理类
    支持用户和系统级别的环境变量增删改查，特别优化了PATH变量处理
    """
    # 注册表路径
    REG_USER_ENV = r"Environment"
    REG_SYSTEM_ENV = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    # 广播消息常量
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    
    def __init__(self,showWarning:bool = False):
        """初始化，检查管理员权限"""
        self.isAdmin = self._checkAdmin()
        self.showWarning=showWarning
        self.errMsg=""
    
    def _checkAdmin(self) -> bool:
        """检查是否具有管理员权限"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    
    def _getRegistryKey(self, level: str, access: int = winreg.KEY_READ):
        """
        获取注册表键
        Args:
            level: 'user' 或 'system'
            access: 访问权限
        Returns:
            注册表键对象
        """
        if level.lower() == 'user':
            return winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.REG_USER_ENV, 0, access)
        elif level.lower() == 'system':
            if not self.isAdmin and access & winreg.KEY_WRITE:
                raise PermissionError("修改系统环境变量需要管理员权限")
            return winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, self.REG_SYSTEM_ENV, 0, access)
        else:
            raise ValueError("level必须是'user'或'system'")
            
    # getter
    @property
    def ErrMsg(self):
        return self.errMsg
    
    def broadcastChange(self):
        """广播环境变量更改，使修改立即生效"""
        ctypes.windll.user32.SendMessageW(
            self.HWND_BROADCAST, 
            self.WM_SETTINGCHANGE, 
            0, 
            "Environment"
        )
    
    def getVariable(self, name: str, level: str = 'user') -> Optional[str]:
        """
        获取环境变量的值
        Args:
            name: 变量名
            level: 'user' 或 'system'
        Returns:
            变量值，如果不存在则返回None
        """
        try:
            with self._getRegistryKey(level, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, name)
                return value
        except FileNotFoundError:
            return None
        except Exception as e:
            self.errMsg=f"获取变量 {name} 失败: {e}"
            return None
    
    def setVariable(self, name: str, value: str, level: str = 'user', broadcast: bool = True):
        """
        设置环境变量（如果存在则覆盖）
        Args:
            name: 变量名
            value: 变量值
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        returns:
            是否成功
        """
        try:
            with self._getRegistryKey(level, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, name, 0, winreg.REG_EXPAND_SZ, value)
            if broadcast:
                self.broadcastChange()
            return True
        except PermissionError as e:
            self.errMsg=f"权限错误: {e}"
            return False
        except Exception as e:
            self.errMsg=f"设置变量失败: {e}"
            return False
    
    def deleteVariable(self, name: str, level: str = 'user', broadcast: bool = True):
        """
        删除环境变量
        Args:
            name: 变量名
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        """
        try:
            with self._getRegistryKey(level, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, name)
            if broadcast:
                self.broadcastChange()
            return True
        except FileNotFoundError:
            self.errMsg=f"变量不存在: {name}"
            return False
        except PermissionError as e:
            self.errMsg=f"权限错误: {e}"
            return False
        except Exception as e:
            self.errMsg=f"删除变量失败: {e}"
            return False
    
    def getPath(self, level: str = 'user') -> List[str]:
        """
        获取PATH变量中的路径列表
        Args:
            level: 'user' 或 'system'
        Returns:
            路径列表
        """
        path_value = self.getVariable('PATH', level)
        if not path_value:
            return []
        # 分割PATH，过滤空字符串
        paths = [p.strip() for p in path_value.split(';') if p.strip()]
        return paths
    
    def setPath(self, paths: List[str], level: str = 'user', broadcast: bool = True):
        """
        设置PATH变量（覆盖原有值）
        Args:
            paths: 路径列表
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        """
        path_value = ';'.join(paths)
        return self.setVariable('PATH', path_value, level, broadcast)
    
    def addToPath(self, folder_path: str, level: str = 'user', broadcast: bool = True):
        """
        向PATH添加文件夹路径
        Args:
            folder_path: 要添加的文件夹路径
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        Returns:
            bool: 是否成功添加
        """
        # 规范化路径
        folder_path = os.path.normpath(folder_path)
        # 检查文件夹是否存在
        if not os.path.exists(folder_path) and self.showWarning:
            print(f"⚠警告: 路径不存在 - {folder_path}")
        
        # 获取当前PATH
        current_paths = self.getPath(level)
        # 检查是否已存在
        if folder_path.lower() in [p.lower() for p in current_paths]:
            self.errMsg=f"路径已存在于{level} PATH中: {folder_path}"
            return False
        # 添加新路径
        current_paths.append(folder_path)
        # 保存新PATH
        success = self.setPath(current_paths, level, broadcast)
        return success
    
    def removeFromPath(self, folder_path: str, level: str = 'user', broadcast: bool = True):
        """
        从PATH中删除文件夹路径
        Args:
            folder_path: 要删除的文件夹路径
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        Returns:
            bool: 是否成功删除
        """
        # 规范化路径
        folder_path = os.path.normpath(folder_path)
        # 获取当前PATH
        current_paths = self.getPath(level)
        # 查找并删除匹配的路径
        original_count = len(current_paths)
        current_paths = [p for p in current_paths if p.lower() != folder_path.lower()]
        if len(current_paths) == original_count:
            self.errMsg=f"路径不存在于{level} PATH中: {folder_path}"
            return False
        # 保存新PATH
        success = self.setPath(current_paths, level, broadcast)
        return success
    
    def addToPath4Multiple(self, folders: List[str], level: str = 'user', broadcast: bool = True):
        """
        批量添加文件夹到PATH
        Args:
            folders: 文件夹路径列表
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        """
        success_count = 0
        for folder in folders:
            if self.addToPath(folder, level, False):
                success_count += 1
        if broadcast and success_count > 0:
            self.broadcastChange()
        return success_count
    
    def removeFromPath4Multiple(self, folders: List[str], level: str = 'user', broadcast: bool = True):
        """
        批量从PATH删除文件夹
        Args:
            folders: 文件夹路径列表
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        """
        success_count = 0
        for folder in folders:
            if self.removeFromPath(folder, level, False):
                success_count += 1
        if broadcast and success_count > 0:
            self.broadcastChange()
        return success_count
    
    def listAllVariables(self, level: str = 'user') -> Dict[str, str]:
        """
        列出所有环境变量
        Args:
            level: 'user' 或 'system'
        Returns:
            变量名:变量值的字典
        """
        variables = {}
        try:
            with self._getRegistryKey(level, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        variables[name] = value
                        i += 1
                    except OSError:
                        break
        except Exception as e:
            self.errMsg=f"列出变量失败: {e}"
        return variables
    
    def backupPath(self, level: str = 'user', backup_file: str | None = None):
        """
        备份当前PATH配置
        Args:
            level: 'user' 或 'system'
            backup_file: 备份文件路径，默认自动生成
        """
        if backup_file is None:
            backup_file = f"path_backup_{level}_{int(os.path.getctime(__file__))}.txt"
        paths = self.getPath(level)
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(f"# PATH备份 - {level}级别\n")
            f.write(f"# 时间: {__import__('datetime').datetime.now()}\n\n")
            for path in paths:
                f.write(f"{path}\n")
        return backup_file
    
    def restorePath(self, backup_file: str, level: str = 'user', broadcast: bool = True):
        """
        从备份文件恢复PATH
        Args:
            backup_file: 备份文件路径
            level: 'user' 或 'system'
            broadcast: 是否广播更改
        """
        if not os.path.exists(backup_file):
            self.errMsg=f"备份文件不存在: {backup_file}"
            return False
        with open(backup_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 过滤注释和空行
        paths = [line.strip() for line in lines 
                if line.strip() and not line.startswith('#')]
        return self.setPath(paths, level, broadcast)
    
    def showPathInfo(self, level: str = 'user'):
        """
        显示PATH详细信息
        """
        paths = self.getPath(level)
        
        print(f"\n{'='*60}")
        print(f"{level.upper()} 级别 PATH 信息")
        print(f"{'='*60}")
        print(f"路径数量: {len(paths)}")
        print(f"\n路径列表:")
        
        for i, path in enumerate(paths, 1):
            exists = "✓" if os.path.exists(path) else "✗"
            print(f"  {i:2d}. [{exists}] {path}")
        
        print(f"{'='*60}\n")
    
    def validatePaths(self, level: str = 'user') -> List[str]:
        """
        验证PATH中的所有路径是否存在
        Returns:
            不存在的路径列表
        """
        paths = self.getPath(level)
        invalid_paths = [p for p in paths if not os.path.exists(p)]
        
        if invalid_paths:
            print(f"\n⚠ 发现 {len(invalid_paths)} 个无效路径:")
            for path in invalid_paths:
                print(f"  - {path}")
        else:
            print(f"✓ 所有 {len(paths)} 个路径都有效")
        
        return invalid_paths