"""
模块：mylog
作者：李生
描述：日志处理
"""
import os
from datetime import datetime
import inspect

class MyLog:
    """日志处理类"""
    def __init__(self, logType="Log",logDir="Logs",retainDays=30):
        self.logDir="Logs"
        if logDir and logDir!="":
            self.logDir=logDir
            if not os.path.exists(logDir):
                os.mkdir(logDir)
        self.retainDays=retainDays
        
    def deleteExpiredLogs(self):
        """删除过期日志"""
        if os.path.exists(self.logDir):
            for filename in os.listdir(self.logDir):
                filePath = os.path.join(self.logDir, filename)
                if os.path.isfile(filePath):
                    fileDate = datetime.strptime(filename.split('-')[1].split('.')[0], "%Y-%m-%d")
                    if (datetime.now() - fileDate).days > self.retainDays:
                        os.remove(filePath)
            
    def _writeLog(self,log,logType="Log"):
        """
        写入日志
        Args:
            log：日志
            kwargs：其他关键字信息
        """
        fileName=os.path.join(self.logDir, logType + "-" + datetime.now().strftime("%Y-%m-%d") + ".txt")
        with open(fileName, 'a', encoding='utf-8') as file:
            file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " => " + log + "\n")
        
    def log(self, log, withCallInfos=True, **kwargs):
        """
        添加常规日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log)
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log)
        else:
            self._writeLog(log)

    def debug(self,log, withCallInfos=True, **kwargs):
        """
        添加调试日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, "Debug")
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, "Debug")
        else:
            self._writeLog(log, "Debug")
            
    def info(self,log, withCallInfos=True, **kwargs):
        """
        添加信息日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, "Info")
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, "Info")
        else:
            self._writeLog(log, "Info")
            
    def warning(self,log, withCallInfos=True, **kwargs):
        """
        添加警告日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, "Warning")
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, "Warning")
        else:
            self._writeLog(log, "Warning")
            
    def error(self,log, withCallInfos=True, **kwargs):
        """
        添加错误日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, "Error")
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, "Error")
        else:
            self._writeLog(log, "Error")
            
    def critical(self,log, withCallInfos=True, **kwargs):
        """
        添加灾难日志
        Args:
            log：日志
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, "Critical")
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, "Critical")
        else:
            self._writeLog(log, "Critical")
            
    def add(self, log, logType="Log", withCallInfos=True, **kwargs):
        """
        添加灾难日志
        Args:
            log：日志
            logType:日志类型
            withCallInfos：是否带上调用信息
            kwargs：其他关键字信息
        """
        if kwargs:
            log += f" | {kwargs}"
        if withCallInfos:    
            callFrame = inspect.currentframe().f_back
            callInfo = inspect.getframeinfo(callFrame)
            if callInfo.function=="<module>":
                self._writeLog(f"{callInfo.filename} > NoFunction > {callInfo.lineno}行" + "：" + log, logType)
            else:
                self._writeLog(f"{callInfo.filename} > {callInfo.function} > {callInfo.lineno}行" + "：" + log, logType)
        else:
            self._writeLog(log, logType)
            