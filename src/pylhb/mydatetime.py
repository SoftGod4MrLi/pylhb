"""
模块：mydatetime
作者：李生
描述：日期时间类
"""
from datetime import datetime, timedelta, date
import calendar
import time

class MyDateTime:
    """日期时间类"""
    def __init__(self,dateTime:date|datetime|str|None=None,formatStr=None) -> None:
        """
        Args:
            dateTime：日期时间
        """
        self.now = self.convert2DateTime(dateTime,formatStr) if dateTime else datetime.now()
        
    @property
    def Year(self):
        """年"""
        return self.now.year
        
    @property
    def Month(self):
        """月"""
        return self.now.month
        
    @property
    def Day(self):
        """日"""
        return self.now.day
        
    @property
    def Hour(self):
        """时"""
        return self.now.hour
        
    @property
    def Minute(self):
        """分"""
        return self.now.minute
        
    @property
    def Second(self):
        """秒"""
        return self.now.second
        
    @property
    def MicroSecond(self):
        """微秒"""
        return self.now.microsecond
        
    @property
    def MilliSecond(self):
        """毫秒"""
        return self.now.microsecond // 1000
    
    @classmethod
    def getToday(cls) -> date:
        """获取今天日期"""
        return datetime.now().date()
        
    @classmethod
    def getYesterday(cls) -> date:
        """获取昨天日期"""
        return cls.getToday() - timedelta(days=1)
        
    @classmethod
    def getTemorrow(cls) -> date:
        """获取明天日期"""
        return cls.getToday() + timedelta(days=1)
        
    @classmethod
    def getAfterTemorrow(cls) -> date:
        """获取后天日期"""
        return cls.getToday() + timedelta(days=2)
        
    @classmethod
    def getCurrentTimestamp(cls):
        """获取当前时间戳"""
        return int(time.time())
        
    @classmethod
    def convertTimestampToDatetime(cls, timestamp):
        """时间戳转换为日期时间"""
        return datetime.fromtimestamp(timestamp)
        
    @classmethod
    def getWeekday(cls, dateTime:date|datetime|str,formatStr=None):
        """获取星期几"""
        return cls.convert2DateTime(dateTime,formatStr).strftime("%A")
        
    @classmethod
    def getChineseWeekday(cls, dateTime:date|datetime|str,formatStr=None):
        """获取中文星期几"""
        date=cls.convert2DateTime(dateTime,formatStr)
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[date.weekday()]
        
    def toDate(self) -> date:
        """获取类日期"""
        return self.now.date()
        
    def toDateTime(self) -> datetime:
        """获取类日期时间"""
        return self.now
        
    def toDateString(self) -> str:
        """获取类日期字符串"""
        return self.now.strftime("%Y-%m-%d")
        
    def toDateTimeString(self) -> str:
        """获取类日期时间字符串"""
        return self.now.strftime("%Y-%m-%d %H:%M:%S")
        
    def toTimeString(self) -> str:
        """获取类时间字符串"""
        return self.now.strftime("%H:%M:%S")
        
    def toString(self,formatStr) -> str:
        """
        到指定格式字符串
        Args:
            formatStr:格式字符串
        Returns:
            指定格式的日期时间字符串
        """
        return self.now.strftime(formatStr)
        
    def addYears(self,years) -> "MyDateTime":
        """
        加年
        Args:
            years:年
        Returns:
            实例
        """
        self.now=self.now.replace(year=self.now.year + years)
        return self
        
    def addMonths(self,months) -> "MyDateTime":
        """
        加月
        Args:
            months:月
        Returns:
            实例
        """
        totalMonths = self.now.month + months
        targetYear = self.now.year + (totalMonths - 1) // 12
        targetMonth = (totalMonths - 1) % 12 + 1
        try:
            self.now = self.now.replace(year=targetYear, month=targetMonth)
        except ValueError:
            # 获取目标月份的最后一天
            if targetMonth == 2:
                # 2月特殊处理（闰年问题）
                import calendar
                last_day = 29 if calendar.isleap(targetYear) else 28
            else:
                # 其他月份：1,3,5,7,8,10,12是31天，4,6,9,11是30天
                last_day = 31 if targetMonth in [1,3,5,7,8,10,12] else 30
            self.now = self.now.replace(year=targetYear, month=targetMonth, day=last_day)
        return self
        
    def addDays(self,days) -> "MyDateTime":
        """
        加日
        Args:
            days:天
        Returns:
            实例
        """
        self.now=self.now + timedelta(days=days)
        return self
        
    def addHours(self,hours) -> "MyDateTime":
        """
        加时
        Args:
            hours:时
        Returns:
            实例
        """
        self.now=self.now + timedelta(hours=hours)
        return self
        
    def addMinutes(self,minutes) -> "MyDateTime":
        """
        加分
        Args:
            minutes:分钟
        Returns:
            实例
        """
        self.now=self.now + timedelta(minutes=minutes)
        return self
        
    def addSeconds(self,seconds) -> "MyDateTime":
        """
        加秒
        Args:
            seconds:秒
        Returns:
            实例
        """
        self.now=self.now + timedelta(seconds=seconds)
        return self
    
    def addMilliSeconds(self,milliseconds) -> "MyDateTime":
        """
        加毫秒
        Args:
            milliseconds：毫秒
        Returns:
            实例
        """
        self.now=self.now + timedelta(milliseconds==milliseconds)
        return self
        
    def addMicroSeconds(self,microseconds) -> "MyDateTime":
        """
        加微秒
        Args:
            microseconds：微秒
        Returns:
            实例
        """
        self.now=self.now + timedelta(microseconds=microseconds)
        return self
        
    
        
    def setDateTime(self,dateTime:date|datetime|str,formatStr=None) -> "MyDateTime":
        """
        设置实例日期时间
        Args:
            dateTime:日期时间，类型可以为date,datetime,str
            formatStr:datetime为字符串时，需要此参数
        Returns:
            实例
        """
        self.now=self.convert2DateTime(dateTime,formatStr)
        return self
        
    @staticmethod
    def convert2DateTime(dateTime,formatStr) -> datetime:
        """
        转DateTime
        Args:
            dateTime:日期时间
            formatStr:格式字符串
        Return:
            datetime
        """
        if isinstance(dateTime, date) and not isinstance(dateTime, datetime):
            return datetime.combine(dateTime, datetime.min.time())
        elif isinstance(dateTime, datetime):
            return dateTime
        elif isinstance(dateTime,str):
            return datetime.strptime(dateTime, formatStr)
        else:
            return datetime.now()
        
    @staticmethod
    def daysDiff(fromDateTime,toDateTime,fromFormatStr=None,toFormatStr=None):
        """
        计算与另一个日期的天数差
        Args:
            fromDateTime:开始日期时间
            toDateTime：结束日期时间
            formatStr:others为字符串时，需要此参数
        """
        fromDT=MyDateTime.convert2DateTime(fromDateTime,fromFormatStr)
        toDT=MyDateTime.convert2DateTime(toDateTime,toFormatStr)
        return abs((toDT - fromDT).days)
        
    @classmethod
    def getMonthFirstDate(cls,year,month) -> date:
        """
        获取指定月份的第一天日期
        Args:
            year:年
            month:月
        Returns:
            月份第一天,
        """
        return date(year, month, 1)
    
    @classmethod
    def getMonthLastDate(cls,year,month) -> date:
        """
        获取指定月份的最后一天日期
        Args:
            year:年
            month:月
        Returns:
            月份最后一天
        """
        return date(year, month, calendar.monthrange(year, month)[1])

    @classmethod
    def getMonthFirstAndLastDate(cls, year: int, month: int) -> tuple[date, date]:
        """
        生成指定月份的第一天和最后一天的日期
        Args:
            year:年
            month:月
        Returns:
            月份第一天,
            月份最后一天
        """
        return cls.getMonthFirstDate(year,month), cls.getMonthLastDate(year,month)
        