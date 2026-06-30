"""
模块：myre
作者：李生
描述：正则判断特殊字符
"""
import re

class MyRe:
    """正则判断特殊字符类，支持手机号、邮箱、身份证、IP地址、邮政编码、网址等验证"""
    
    # 手机号码正则（中国大陆）
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
    
    # 邮箱正则
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # 身份证号码正则（18位或15位）
    ID_CARD_PATTERN = re.compile(r'^[1-9]\d{5}(18|19|20)?\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}(\d|X|x)$')
    
    # IPv4地址正则
    IPV4_PATTERN = re.compile(
        r'^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    # IPv6地址正则（完整格式和压缩格式）
    IPV6_PATTERN = re.compile(
        r'^(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,7}:|'
        r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
        r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
        r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
        r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
        r':((:[0-9a-fA-F]{1,4}){1,7}|:)|'
        r'fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]+|'
        r'::(ffff(:0{1,4})?:)?((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))$'
    )
    
    # 中国大陆邮政编码正则（6位数字）
    POSTCODE_PATTERN = re.compile(r'^[1-9]\d{5}$')
    
    # 网址正则（支持http、https、ftp）
    URL_PATTERN = re.compile(
        r'^(https?|ftp)://'  # 协议
        r'(([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP地址
        r'(:\d+)?'  # 端口
        r'(/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?$',  # 路径
        re.IGNORECASE
    )
    
    @classmethod
    def isPhone(cls, value: str) -> bool:
        """验证是否为有效的手机号码（中国大陆）"""
        return bool(cls.PHONE_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isEmail(cls, value: str) -> bool:
        """验证是否为有效的邮箱地址"""
        return bool(cls.EMAIL_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isIDCard(cls, value: str) -> bool:
        """验证是否为有效的身份证号码（15位或18位，含校验位）"""
        value = value.strip().upper()
        if not cls.ID_CARD_PATTERN.fullmatch(value):
            return False
        
        # 18位身份证需要验证校验码
        if len(value) == 18:
            return cls._verifyIDCard18(value)
        return True
    
    @classmethod
    def _verifyIDCard18(cls, id_card: str) -> bool:
        """验证18位身份证的校验码"""
        factors = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        checksums = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        total = sum(int(id_card[i]) * factors[i] for i in range(17))
        return checksums[total % 11] == id_card[17]
    
    @classmethod
    def isIPv4(cls, value: str) -> bool:
        """验证是否为有效的IPv4地址"""
        return bool(cls.IPV4_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isIPv6(cls, value: str) -> bool:
        """验证是否为有效的IPv6地址"""
        return bool(cls.IPV6_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isPostCode(cls, value: str) -> bool:
        """验证是否为有效的邮政编码（中国大陆）"""
        return bool(cls.POSTCODE_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isURL(cls, value: str) -> bool:
        """验证是否为有效的网址"""
        return bool(cls.URL_PATTERN.fullmatch(value.strip()))
    
    @classmethod
    def isIP(cls, value: str) -> bool:
        """验证是否为有效的IP地址（IPv4或IPv6）"""
        return cls.isIPv4(value) or cls.isIPv6(value)
    