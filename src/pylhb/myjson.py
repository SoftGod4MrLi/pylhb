"""
模块：myjson
作者：李生
描述：JOSN读写
"""
import json

class MyJSON:
    """JSON读写类"""
    def __init__(self,jsonFile="config.json") -> None:
        self.jsonFile=jsonFile
        
    def getKey(self,key):
        """
        获取Key
        Args:
            key:Key
        Returns:此key的数据
        """
        try:
            with open(self.jsonFile,'r', encoding="utf-8") as f:
                configs=json.load(f)
            return configs[key]
        except Exception as e:
           return None 
    
    def setKey(self,key,value) -> bool:
        """
        设置Key
        Args:
            key：key
            value：值
        """
        try:
            # 读取
            with open(self.jsonFile,'r', encoding="utf-8") as f:
                configs=json.load(f)
            # 设置参数
            configs[key]=value
            # 保存
            with open(self.jsonFile, 'w', encoding="utf-8") as f:
                json.dump(configs, f)
            return True
        except Exception as e:
            return False
            
    def deleteKey(self,key) -> bool:
        """
        删除Key
        Args:
            key：key
        """
        try:
            # 读取
            with open(self.jsonFile,'r', encoding="utf-8") as f:
                configs=json.load(f)
            # 删除
            configs.pop(key)
            # 保存
            with open(self.jsonFile, 'w', encoding="utf-8") as f:
                json.dump(configs, f)
            return True
        except Exception as e:
            return False