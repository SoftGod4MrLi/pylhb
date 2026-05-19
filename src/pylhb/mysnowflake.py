"""
模块：mysnowflake
作者：李生
描述：雪花ID
"""
import time

class MySnowflake:
    """雪花ID类"""
    # 基本参数
    epoch = 1609459200000 # 自定义的开始时间（2021-01-01 00:00:00）
    worker_id_bits = 10 # 工作机器ID占用的位数
    datacenter_id_bits = 10 # 数据中心ID占用的位数
    sequence_bits = 12 # 序列号占用的位数

    # 计算各部分的位移
    worker_id_shift = sequence_bits # 序列号位移
    datacenter_id_shift = sequence_bits + worker_id_bits # 数据中心ID位移
    timestamp_shift = sequence_bits + worker_id_bits + datacenter_id_bits # 时间戳位移

    # 生成掩码
    max_worker_id = -1 ^ (-1 << worker_id_bits) # 计算最大工作机器ID
    max_datacenter_id = -1 ^ (-1 << datacenter_id_bits) # 计算最大数据中心ID
    sequence_mask = -1 ^ (-1 << sequence_bits) # 计算序列号掩码

    def __init__(self, worker_id = 1, datacenter_id = 1):
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f'worker_id必须在0到{self.max_worker_id}之间')
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f'datacenter_id必须在0到{self.max_datacenter_id}之间')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = 0 # 序列号初始值
        self.last_timestamp = -1 # 上一次生成ID的时间戳

    def _current_time_millis(self):
        return int(time.time() * 1000) # 获取当前时间戳（毫秒）

    def generateID(self):
        """生成雪花ID"""
        timestamp = self._current_time_millis() # 获取当前时间戳

        if timestamp < self.last_timestamp:
            raise Exception('时钟向后移动，无法生成ID')

        if self.last_timestamp == timestamp:
            self.sequence = (self.sequence + 1) & self.sequence_mask # 在同一毫秒内序列号加1
        if self.sequence == 0:
        # 序列号已满，等待下一毫秒
            while timestamp <= self.last_timestamp:
                timestamp = self._current_time_millis()
        else:
            equence = 0 # 重置序列号

        self.last_timestamp = timestamp # 更新上一次时间戳

        # 生成ID
        id = ((timestamp - self.epoch) << self.timestamp_shift) | \
        (self.datacenter_id << self.datacenter_id_shift) | \
        (self.worker_id << self.worker_id_shift) | \
        self.sequence
        return id