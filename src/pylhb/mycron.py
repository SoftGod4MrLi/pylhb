"""
模块：mycron
作者：李生
描述：Cron表达式解析
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Union

class MyCron:
    """
    Cron表达式解析类
    支持标准Cron格式：分 时 日 月 周
    支持特殊字符：* , - / ? L W #
    """
    # 月份映射
    MONTHS = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    
    # 星期映射
    WEEKDAYS = {
        'SUN': 0, 'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6
    }
    
    def __init__(self, cron_expression: str):
        """
        初始化Cron表达式解析器
        
        Args:
            cron_expression: Cron表达式字符串，格式：分 时 日 月 周
        """
        self.expression = cron_expression.strip()
        self.fields = self._parseExpression()
        
    def _parseExpression(self) -> List[str]:
        """解析Cron表达式为字段列表"""
        fields = self.expression.split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron expression: {self.expression}. Expected 5 fields, got {len(fields)}")
        return fields
    
    def _parseField(self, field: str, min_val: int, max_val: int, 
                     special_chars: str = '', name_map: dict | None = None) -> List[int]:
        """
        解析单个字段
        Args:
            field: 字段字符串
            min_val: 最小值
            max_val: 最大值
            special_chars: 允许的特殊字符
            name_map: 名称映射（用于月份和星期）
        Returns:
            解析后的值列表
        """
        if field == '*':
            return list(range(min_val, max_val + 1))
        
        # 处理名称映射
        if name_map:
            for name, value in name_map.items():
                field = field.replace(name, str(value))
        
        values = set()
        
        # 处理特殊字符
        if ',' in field:
            # 列表
            parts = field.split(',')
            for part in parts:
                values.update(self._parseField(part, min_val, max_val))
        elif '/' in field:
            # 步长
            base, step = field.split('/')
            step = int(step)
            if base == '*':
                start = min_val
            else:
                start = int(base)
            values.update(range(start, max_val + 1, step))
        elif '-' in field:
            # 范围
            start, end = map(int, field.split('-'))
            values.update(range(start, end + 1))
        elif field == '?':
            # 问号 (用于日或周，表示不指定)
            return []
        else:
            # 单个值
            values.add(int(field))
        
        # 验证值范围
        for val in values:
            if val < min_val or val > max_val:
                raise ValueError(f"Value {val} out of range [{min_val}, {max_val}]")
        
        return sorted(list(values))
    
    def parseMinute(self) -> List[int]:
        """解析分钟字段 (0-59)"""
        return self._parseField(self.fields[0], 0, 59)
    
    def parseHour(self) -> List[int]:
        """解析小时字段 (0-23)"""
        return self._parseField(self.fields[1], 0, 23)
    
    def parseDay(self) -> List[int]:
        """解析日期字段 (1-31)"""
        if self.fields[2] == '?':
            return []
        return self._parseField(self.fields[2], 1, 31, special_chars='?L#')
    
    def parseMonth(self) -> List[int]:
        """解析月份字段 (1-12)"""
        return self._parseField(self.fields[3], 1, 12, name_map=self.MONTHS)
    
    def parseWeekday(self) -> List[int]:
        """解析星期字段 (0-6, 0=周日)"""
        if self.fields[4] == '?':
            return []
        return self._parseField(self.fields[4], 0, 6, name_map=self.WEEKDAYS)
    
    def getAllValues(self) -> dict:
        """获取所有解析后的值"""
        return {
            'minute': self.parseMinute(),
            'hour': self.parseHour(),
            'day': self.parseDay(),
            'month': self.parseMonth(),
            'weekday': self.parseWeekday()
        }
    
    def getNextExecution(self, from_time: datetime | None = None, max_attempts: int = 1000) -> Optional[datetime]:
        """
        获取下一次执行时间
        
        Args:
            from_time: 起始时间，默认为当前时间
            max_attempts: 最大尝试次数，防止无限循环
        
        Returns:
            下一次执行时间，如果没有则返回None
        """
        if from_time is None:
            from_time = datetime.now()
        
        # 获取解析后的值
        minutes = self.parseMinute()
        hours = self.parseHour()
        days = self.parseDay()
        months = self.parseMonth()
        weekdays = self.parseWeekday()
        
        # 从下一秒开始检查
        current = from_time + timedelta(seconds=1)
        
        for _ in range(max_attempts):
            # 检查月份
            if months and current.month not in months:
                current = self._nextMonth(current)
                continue
            
            # 检查日期和星期
            if days and weekdays:
                # 同时指定日和星期，需要同时满足
                day_match = current.day in days
                weekday_match = current.weekday() in weekdays
                if not (day_match or weekday_match):
                    current = self._nextDay(current)
                    continue
            elif days:
                if current.day not in days:
                    current = self._nextDay(current)
                    continue
            elif weekdays:
                if current.weekday() not in weekdays:
                    current = self._nextDay(current)
                    continue
            
            # 检查小时
            if current.hour not in hours:
                current = self._nextHour(current)
                continue
            
            # 检查分钟
            if current.minute not in minutes:
                current = self._nextMinute(current)
                continue
            
            # 所有条件满足
            # 将秒和微秒归零
            return current.replace(second=0, microsecond=0)
        
        return None
    
    def _nextMinute(self, dt: datetime) -> datetime:
        """获取下一分钟"""
        return dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
    
    def _nextHour(self, dt: datetime) -> datetime:
        """获取下一小时"""
        return dt.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    
    def _nextDay(self, dt: datetime) -> datetime:
        """获取下一天"""
        return dt.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _nextMonth(self, dt: datetime) -> datetime:
        """获取下一个月"""
        if dt.month == 12:
            return dt.replace(year=dt.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return dt.replace(month=dt.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    def getFutureExecutions(self, count: int = 5, from_time: datetime | None = None) -> List[datetime]:
        """
        获取未来多次执行时间
        Args:
            count: 获取次数
            from_time: 起始时间
        Returns:
            未来执行时间列表
        """
        executions = []
        current = from_time

        if current:
            for _ in range(count):
                next_time = self.getNextExecution(current)
                if next_time:
                    executions.append(next_time)
                    current = next_time + timedelta(seconds=1)
                else:
                    break
        
        return executions
    
    def __str__(self) -> str:
        """返回Cron表达式字符串"""
        return self.expression
    
    def toCrontabFormat(self) -> str:
        """返回crontab格式的字符串"""
        return f"{self.fields[0]} {self.fields[1]} {self.fields[2]} {self.fields[3]} {self.fields[4]}"
