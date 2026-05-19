"""
模块：myini
作者：李生
描述：INI配置文件读写
"""
import configparser
import os

class MyINI:
    """配置文件管理类"""
    def __init__(self, configFile="config.ini"):
        self.configFile = configFile
        if not os.path.exists(self.configFile):
            with open(self.configFile, 'w', encoding='gb2312') as f:
                f.write("[main]\n")
        self.cf = configparser.ConfigParser()
        self.cf.read(self.configFile, encoding='gb2312')

    def get(self, section, key,defaultValue=""):
        """
        获取节点值
        Args:
            section：节点
            key：键
            defaultValue：默认值
        Returns:
            值
        """
        if self.cf.has_section(section) and self.cf.has_option(section, key):
            return self.cf.get(section, key)
        return defaultValue

    def set(self, section, key, value):
        """
        设置节点值
        Args:
            section：节点
            key：键
            value：值
        """
        if self.cf.has_section(section) is False:
            self.cf.add_section(section)
        self.cf.set(section, key, value)
        with open(self.configFile, 'w', encoding='gb2312') as f:
            self.cf.write(f)
            
    def remove(self, section, key):
        """
        删除节点
        Args:
            section：节点
            key：键
        """
        self.cf.remove_option(section, key)
        with open(self.configFile, 'w', encoding='gb2312') as f:
            self.cf.write(f)
            
    