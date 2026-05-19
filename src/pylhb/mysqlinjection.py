"""
模块：mysqlinjection
作者：李生
描述：SQL注入检查
"""
import re
from typing import List, Tuple, Optional

class MySQLInjection:
    """
    SQL注入检查类
    检测SQL语句中是否存在潜在的注入风险
    """
    
    # 常见的SQL注入关键字模式
    SQL_KEYWORDS_PATTERNS = [
        r'\bUNION\b.*\bSELECT\b',
        r'\bSELECT\b.*\bFROM\b',
        r'\bINSERT\b.*\bINTO\b',
        r'\bUPDATE\b.*\bSET\b',
        r'\bDELETE\b.*\bFROM\b',
        r'\bDROP\b.*\bTABLE\b',
        r'\bCREATE\b.*\bTABLE\b',
        r'\bALTER\b.*\bTABLE\b',
        r'\bEXEC\b.*\bXP_',
        r'\bEXECUTE\b.*\bXP_',
        r'\bOR\b.*\b1\s*=\s*1\b',
        r'\bOR\b.*\bTRUE\b',
        r'\bAND\b.*\b1\s*=\s*1\b',
        r'\bAND\b.*\bTRUE\b',
        r'\b--\b',  # SQL注释
        r'/\*.*\*/',  # 多行注释
        r';.*\bDROP\b',
        r'\bWAITFOR\b.*\bDELAY\b',
        r'\bBENCHMARK\b\(',
        r'\bSLEEP\b\(',
        r'\bLOAD_FILE\b\(',
        r'\bINTO\s+OUTFILE\b',
        r'\bINTO\s+DUMPFILE\b',
    ]
    
    # 危险字符模式
    DANGEROUS_CHARS_PATTERNS = [
        r"'.*'.*'.*'",  # 多个引号
        r'".*".*".*"',  # 多个双引号
        r'\\x[0-9A-Fa-f]{2}',  # 十六进制编码
        r'\\u[0-9A-Fa-f]{4}',  # Unicode编码
        r'%[0-9A-Fa-f]{2}',  # URL编码
    ]
    
    # 常见SQL注入负载模式
    PAYLOAD_PATTERNS = [
        r"'\s+OR\s+'1'\s*=\s*'1",
        r'\"\s+OR\s+\"1\"\s*=\s*\"1',
        r"'\s+OR\s+1\s*=\s*1\s*--",
        r'\"\s+OR\s+1\s*=\s*1\s*--',
        r"'\s+UNION\s+SELECT\s+",
        r'\"\s+UNION\s+SELECT\s+',
        r"'\s+AND\s+\(?SELECT",
        r'\bSLEEP\s*\(\s*\d+\s*\)',
        r'\bBENCHMARK\s*\(\s*\d+\s*,',
        r'\bWAITFOR\s+DELAY\s+\'[0-9:]+\'',
        r"';\s*DROP\s+TABLE",
        r'\"\s*;\s*DROP\s+TABLE',
    ]
    
    def __init__(self, case_sensitive: bool = False):
        """
        初始化检测器
        Args:
            case_sensitive: 是否区分大小写，默认False（不区分）
        """
        self.case_sensitive = case_sensitive
        self.flags = 0 if case_sensitive else re.IGNORECASE
        self._compilePatterns()
    
    def _compilePatterns(self):
        """预编译所有正则表达式模式以提高性能"""
        self.keyword_patterns = [
            (pattern, re.compile(pattern, self.flags))
            for pattern in self.SQL_KEYWORDS_PATTERNS
        ]
        self.dangerous_patterns = [
            (pattern, re.compile(pattern, self.flags))
            for pattern in self.DANGEROUS_CHARS_PATTERNS
        ]
        self.payload_patterns = [
            (pattern, re.compile(pattern, self.flags))
            for pattern in self.PAYLOAD_PATTERNS
        ]
    
    def detect(self, sqlStr: str) -> tuple[bool, List[str], float]:
        """
        检测SQL字符串是否存在注入风险
        Args:
            sqlStr: 待检测的SQL字符串
        Returns:
            Tuple[bool, List[str], float]: 
                - 是否存在注入风险
                - 检测到的威胁列表
                - 风险分数 (0-100)
        """
        if not sqlStr or not isinstance(sqlStr, str):
            return False, [], 0.0
        
        threats = []
        risk_score = 0.0
        
        # 检查关键字模式
        for pattern_name, pattern in self.keyword_patterns:
            if pattern.search(sqlStr):
                threats.append(f"危险SQL关键字: {pattern_name}")
                risk_score += 15
        
        # 检查危险字符模式
        for pattern_name, pattern in self.dangerous_patterns:
            if pattern.search(sqlStr):
                threats.append(f"危险字符模式: {pattern_name}")
                risk_score += 10
        
        # 检查注入负载模式
        for pattern_name, pattern in self.payload_patterns:
            if pattern.search(sqlStr):
                threats.append(f"SQL注入负载: {pattern_name}")
                risk_score += 25
        
        # 检查引号不匹配（可能的注入尝试）
        if self._checkUnmatchedQuotes(sqlStr):
            threats.append("引号不匹配，可能存在注入尝试")
            risk_score += 20
        
        # 检查特殊字符过多
        special_char_ratio = self._calculateSpecialCharRatio(sqlStr)
        if special_char_ratio > 0.3:
            threats.append(f"特殊字符比例过高: {special_char_ratio:.2%}")
            risk_score += special_char_ratio * 50
        
        # 限制最高分数为100
        risk_score = min(risk_score, 100.0)
        
        # 判断是否存在注入风险（风险分数超过阈值）
        is_injection = risk_score >= 30.0
        
        return is_injection, threats, risk_score
    
    def _checkUnmatchedQuotes(self, sqlStr: str) -> bool:
        """检查引号是否匹配"""
        single_quotes = sqlStr.count("'")
        double_quotes = sqlStr.count('"')
        # 奇数个引号表示不匹配
        return (single_quotes % 2 != 0) or (double_quotes % 2 != 0)
    
    def _calculateSpecialCharRatio(self, sqlStr: str) -> float:
        """计算特殊字符比例"""
        special_chars = set("'\"`;--#%&*+=<>()/\\|[]{}")
        special_count = sum(1 for char in sqlStr if char in special_chars)
        total_length = len(sqlStr)
        
        if total_length == 0:
            return 0.0
        
        return special_count / total_length
    
    @classmethod
    def getRiskLevel(cls, score: float) -> str:
        """
        获取风险等级
        Args:
            score: 风险分数
        Returns:
            str: 风险等级 (安全/低风险/中风险/高风险)
        """
        if score < 20:
            return "安全"
        elif score < 50:
            return "低风险"
        elif score < 75:
            return "中风险"
        else:
            return "高风险"
    