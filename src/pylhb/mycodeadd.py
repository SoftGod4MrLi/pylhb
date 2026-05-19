"""
模块：mycodeadd
作者：李生
描述：编码相加类
"""
class MyCodeAdd:
    """编码相加类"""
    def addCode(code: str, step: int = 1) -> str:
        """将编码右边的数字部分增加指定步长，如 'A001' 步长2 -> 'A003'
        Args:
            code: 原始编码字符串
            step: 增加的步长，默认为1
        Returns: 
            增加后的编码字符串
        """
        # 从右向左找到第一个非数字字符的位置
        i = len(code) - 1
        while i >= 0 and code[i].isdigit():
            i -= 1
        # 分割前缀和数字部分
        prefix = code[:i+1]
        num_part = code[i+1:]
        # 如果没有数字部分，默认当作0处理
        if not num_part:
            num_part = "0"
        # 数字增加指定步长，并保持原宽度（前导零）
        new_num = int(num_part) + step
        width = len(num_part)
        new_num_str = str(new_num).zfill(width)
        return prefix + new_num_str