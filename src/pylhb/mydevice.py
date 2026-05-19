"""
模块：mydevice
作者：李生
描述：设备信息管理
"""
import uuid
import hashlib
import socket
import subprocess
import platform

class MyDevice:
    """设备信息管理类"""
    def getHostName(self) -> str:
        """获取主机名称"""
        return socket.gethostname()
        
    def getDeviceID(self,withWindowsCPUID:bool = False,withWindowsBoardID:bool=True) -> str:
        """
        获取设备ID
        Args:
            withWindowsCPUID：Windows下使用CPU序列号
            withWindowsBoardID：Windows下使用主板序列号
        Returns:
            设备ID
        """
        deviceinfos=[]
        # 如果要获取CPD序列号
        if platform.system()=="Windows":
            # 获取CPU序列号
            if withWindowsCPUID:
                cpuid=self.getWindowsCPUID()
                if cpuid:
                    deviceinfos.append(cpuid)
            # 获取主板序列号
            if withWindowsBoardID:
                boardID=self.getWindowsBoardID()
                if boardID:
                    deviceinfos.append(boardID)
        elif platform.system()=="Linux":
            # 获取MachineID
            machineid=self.getLinuxMachineID()
            if machineid:
                deviceinfos.append(machineid)
        else:
            pass
            
        # 如果还有信息，就获取MAC地址
        if len(deviceinfos)==0:
            macAddress=self.getMAC()
            if macAddress:
                deviceinfos.append(macAddress)
        
        # 如果还是没有信息，就直接Unknown
        if len(deviceinfos)==0:
            deviceinfos.append("Unknown")
            
        # 拼接为字符串
        deviceinfostr = "".join(deviceinfos)
        
        return hashlib.md5(deviceinfostr.encode()).hexdigest()
        
    def getWindowsCPUID(self) -> str:
        """获取Windows的CPU序列号（用的是PowerShell不是wmic）"""
        try:
            cmd = [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty ProcessorId"
            ]
            out = subprocess.check_output(cmd, text=True, encoding='gbk', errors='ignore').strip()
            return out if out else None
        except:
            return None
            
    def getWindowsBoardID(self) -> str:
        """获取Windows主板序列号"""
        try:
            cmd = [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_BaseBoard | Select-Object -ExpandProperty SerialNumber"
            ]
            out = subprocess.check_output(cmd, text=True, encoding='gbk', errors='ignore').strip()
            return out if out else None
        except:
            return None
            
    def getWindowsUUID(self) -> str:
        """获取Windows系统UUID"""
        try:
            cmd = [
                "powershell",
                "-Command",
                "Get-CimInstance Win32_ComputerSystemProduct | Select-Object -ExpandProperty UUID"
            ]
            out = subprocess.check_output(cmd, text=True, encoding='gbk', errors='ignore').strip()
            return out if out else None
        except:
            return None
            
    def getLinuxMachineID(slef) -> str:
        """获取Linux的MachineID"""
        try:
            with open("/etc/machine-id", "r") as f:
                mid = f.read().strip()
            return mid if len(mid) == 32 else None
        except:
            return None
        
    def getMAC(self) -> str:
        """获取MAC地址"""
        try:
            mac = uuid.getnode()
            return ':'.join(['{:02x}'.format((mac >> elements) & 0xff) for elements in range(0,8*6,8)][::-1])
        except:
            return None
            
    def getLocalIP(self) -> str:
        """获取本地IP地址"""
        try:
            # 创建一个socket连接（实际上不会发送数据）
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"