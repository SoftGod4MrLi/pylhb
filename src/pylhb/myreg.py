"""
模块：myreg
作者：李生
描述：注册表读写
"""
import winreg
from typing import Any

class MyReg:
    """注册表读写类"""
    def get(self,valueName,root=winreg.HKEY_CURRENT_USER,path=r"Software\BDSoftGod")-> tuple[bool, Any, int]:
        """
        读取
        Args:
            vakueName：数值名称
            root：根
            path：路径
        Returns:
            是否成功
            数据
            数据类型
        """
        try:
            # 使用 with 语句打开键，确保自动关闭，这是推荐的最佳实践[citation:7]
            # 0 是保留参数，必须为0。KEY_READ 指定只读权限
            with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
                # 读取值，返回一个元组 (数据, 数据类型)
                data, regType = winreg.QueryValueEx(key, valueName)
                return True,data,regType
        except FileNotFoundError:
            return False,"路径或值未找到。",0
        except PermissionError:
            return False,"权限不足。",0
        except Exception as e:
            return False,"{e}",0
            
    def __getRegType(self,data):
        """
        获取数据的类型
        Args:
            data：数据
        Returns:
            数据类型
            处理过的数据
        """
        data_type = type(data)
        # 处理布尔值
        if isinstance(data, bool):
            return winreg.REG_DWORD, 1 if data else 0
        # 处理整数（确保在 DWORD 范围内）
        if isinstance(data, int):
            if data < 0 or data > 4294967295:
                return winreg.REG_QWORD, data  # 超出范围用64位整数
            return winreg.REG_DWORD, data
        # 处理字符串（检查是否包含多行）
        if isinstance(data, str):
            if '\n' in data or '\0' in data:
                # 包含换行符，可能想用多字符串
                parts = data.replace('\0', '\n').split('\n')
                parts = [p for p in parts if p]  # 过滤空字符串
                if len(parts) > 1:
                    return winreg.REG_MULTI_SZ, parts
            return winreg.REG_SZ, data
        # 处理列表
        if isinstance(data, list):
            # 检查是否都是字符串
            if all(isinstance(item, str) for item in data):
                return winreg.REG_MULTI_SZ, data
            else:
                # 转换为字符串列表
                return winreg.REG_MULTI_SZ, [str(item) for item in data]
        # 处理字节
        if isinstance(data, bytes):
            return winreg.REG_BINARY, data
        # 处理 None
        if data is None:
            return winreg.REG_NONE, b''
        # 默认当作字符串处理
        return winreg.REG_SZ, str(data)
        
    def set(self,valueName,valueData,root=winreg.HKEY_CURRENT_USER,path=r"Software\BDSoftGod"):
        """
        写入/修改
        Args:
            vakueName：数值名称
            valueData：数值数据
            root：根
            path：路径
        Returns:
            是否成功
            执行结果 
        """
        try:
            regType, processedData = self.__getRegType(valueData)
            with winreg.CreateKey(root, path) as key:
                winreg.SetValueEx(key, valueName, 0, regType, processedData)
                return True,"OK"
        except PermissionError:
            return False,"权限不足。"
        except TypeError:
            return False,"类型错误。"
        except Exception as e:
            return False,"{e}"
            
    def deleteData(self,valueName,root=winreg.HKEY_CURRENT_USER,path=r"Software\BDSoftGod") -> tuple[bool,str]:
        """
        删除数据
        Args:
            vakueName：数值名称
            root：根
            path：路径
        Returns:
            是否成功
        """
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
                winreg.DeleteValue(key, valueName)
                return True,"OK"
        except FileNotFoundError:
            return False,"路径或值未找到。"
        except PermissionError:
            return False,"权限不足。"
        except Exception as e:
            return False,"{e}"

    def deleteSubKey(self,subkeyName,root=winreg.HKEY_CURRENT_USER,path=r"Software\BDSoftGod") -> tuple[bool,str]:
        """
        删除子键
        Args:
            subkeyName：子键名称
            root：根
            path：路径
        Returns:
            是否成功
            执行结果
        """
        fullPath = f"{path}\\{subkeyName}" if path else subkeyName
        try:
            winreg.DeleteKey(root, fullPath)
            return True,"OK"
        except FileNotFoundError:
            return False,"子键不存在。"
        except PermissionError:
            return False,"权限不足。"
        except Exception as e:
            return False,"{e}"
            
    def deleteKey(self,root=winreg.HKEY_CURRENT_USER,path=r"Software\BDSoftGod"):
        """
        删除键及其所有子键
        Args:
            root：根
            path：路径
        Returns:
            是否成功
            执行结果
        """
        try:
            with winreg.OpenKey(root, path, 0, winreg.KEY_ALL_ACCESS) as key:
                # 获取所有子键名称
                subkeys = []
                index = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, index)
                        subkeys.append(subkey_name)
                        index += 1
                    except OSError:
                        break
                # 递归删除所有子键
                for subkey in subkeys:
                    subkey_path = f"{path}\\{subkey}" if path else subkey
                    self.deleteKey(root, subkey_path)
            # 删除当前键（此时已经没有子键了）
            winreg.DeleteKey(root, path)
            return True,"OK"
        except FileNotFoundError:
            return False,"键不存在。"
        except PermissionError:
            return False,"权限不足。"
        except Exception as e:
            return False,"{e}"