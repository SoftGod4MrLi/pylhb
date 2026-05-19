"""
模块：mycipher
作者：李生
描述：加解密管理
"""
import hashlib
import base64
from typing import Union
import secrets

class MyAsymClipher:
    """非对称加密类"""
    def md5(self,text):
        """
        MD5
        Args
            text：明文
        Returns:
            明文的MD5
        """
        mdFive = hashlib.md5()
        mdFive.update(text.encode('utf-8'))
        encrypted_text = mdFive.hexdigest()
        return encrypted_text
        
    def sha256(self,text):
        """
        sha256
        Args:
            text：明文
        Returns:
            明文的sha256
        """
        sha = hashlib.sha256()
        sha.update(text.encode('utf-8'))
        encrypted_text = sha.hexdigest()
        return encrypted_text
        
class MyXORCipher:
    """XOR对称加解密类"""
    def __init__(self, key: Union[str, bytes]):
        # 将key转换为字节
        if isinstance(key, str):
            key = key.encode('utf-8')
        self.key = key
    
    def _xor_encrypt(self, data: bytes) -> bytes:
        """XOR加密/解密的核心算法"""
        # 重复key以匹配数据长度
        repeated_key = (self.key * (len(data) // len(self.key) + 1))[:len(data)]
        return bytes(a ^ b for a, b in zip(data, repeated_key))
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密
        Args:
            data：明文
        Returns:
            XOR密文
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        encrypted = self._xor_encrypt(data)
        return base64.b64encode(encrypted).decode('utf-8')
        
    def decrypt(self, encryptedData: str) -> str:
        """
        解密
        Args:
            encryptedData：XOR密文
        Returns:
        明文
        """
        if not encryptedData:
            return ""
        data = base64.b64decode(encryptedData)
        decrypted = self._xor_encrypt(data)
        return decrypted.decode('utf-8')
        
class MyFernetCipher:
    """类似于Fernet的对称加解密类"""
    def __init__(self, key: Union[str, bytes]):
        if isinstance(key, str):
            key = key.encode('utf-8')
        # 使用PBKDF2派生密钥
        self.salt = secrets.token_bytes(16)
        self.key = hashlib.pbkdf2_hmac('sha256', key, self.salt, 100000, dklen=32)
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密
        Args:
            data：明文
        RReturns:
            Fernet密文
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # 生成随机IV
        iv = secrets.token_bytes(16)
        
        # 简单的加密：使用密钥和IV进行XOR
        combined_key = hashlib.sha256(self.key + iv).digest()
        
        # 重复密钥以匹配数据长度
        repeated_key = (combined_key * (len(data) // len(combined_key) + 1))[:len(data)]
        encrypted = bytes(a ^ b for a, b in zip(data, repeated_key))
        
        # 组合盐值、IV和加密数据
        result = self.salt + iv + encrypted
        return base64.b64encode(result).decode('utf-8')
    
    def decrypt(self, encryptedData: str) -> str:
        """
        解密
        Args:
            encryptedData：Fernet密文
        Returns:
            明文
        """
        if not encryptedData:
            return ""
        data = base64.b64decode(encryptedData)
        
        # 提取盐值、IV和加密数据
        self.salt = data[:16]
        iv = data[16:32]
        encrypted = data[32:]
        
        # 重新生成密钥
        if hasattr(self, 'key'):
            # 保留原密钥
            pass
        else:
            raise ValueError("需要重新初始化密码")
        
        # 解密
        combined_key = hashlib.sha256(self.key + iv).digest()
        repeated_key = (combined_key * (len(encrypted) // len(combined_key) + 1))[:len(encrypted)]
        decrypted = bytes(a ^ b for a, b in zip(encrypted, repeated_key))
        
        return decrypted.decode('utf-8')
        
class MyBlowfishCipher:
    """Blowfish的简单分组加解密类"""
    def __init__(self, key: Union[str, bytes]):
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        # 生成子密钥
        self.subkeys = self._generate_subkeys(key)
        self.block_size = 8  # 64位块
    
    def _generate_subkeys(self, key: bytes) -> list:
        """生成18个32位子密钥"""
        subkeys = []
        # 使用SHA256哈希生成子密钥
        hash_input = key
        for i in range(18):
            hash_result = hashlib.sha256(hash_input + str(i).encode()).digest()
            # 取前4字节作为32位子密钥
            subkey = int.from_bytes(hash_result[:4], 'big')
            subkeys.append(subkey)
        return subkeys
    
    def _feistel_round(self, half_block: int, subkey: int) -> int:
        """Feistel轮函数"""
        # 简化的轮函数：XOR和哈希
        combined = (half_block ^ subkey).to_bytes(8, 'big')
        hash_result = hashlib.sha256(combined).digest()[:4]
        return int.from_bytes(hash_result, 'big')
    
    def _encrypt_block(self, block: bytes) -> bytes:
        """加密一个8字节块"""
        if len(block) != 8:
            raise ValueError("块大小必须是8字节")
        
        # 将块分为左右两半
        left = int.from_bytes(block[:4], 'big')
        right = int.from_bytes(block[4:], 'big')
        
        # 16轮Feistel网络
        for i in range(16):
            left, right = right, left ^ self._feistel_round(right, self.subkeys[i])
        
        # 最后一轮交换
        left, right = right, left
        
        # 合并
        return left.to_bytes(4, 'big') + right.to_bytes(4, 'big')
    
    def _decrypt_block(self, block: bytes) -> bytes:
        """解密一个8字节块"""
        if len(block) != 8:
            raise ValueError("块大小必须是8字节")
        
        left = int.from_bytes(block[:4], 'big')
        right = int.from_bytes(block[4:], 'big')
        
        # 反向16轮Feistel网络
        for i in range(15, -1, -1):
            left, right = right, left ^ self._feistel_round(right, self.subkeys[i])
        
        # 最后一轮交换
        left, right = right, left
        
        return left.to_bytes(4, 'big') + right.to_bytes(4, 'big')
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """
        加密
        Args:
            data：明文
        Returns:
            Blowfish密文
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # PKCS7填充
        padding_len = self.block_size - (len(data) % self.block_size)
        data += bytes([padding_len]) * padding_len
        
        # 分块加密
        encrypted = b''
        for i in range(0, len(data), self.block_size):
            block = data[i:i + self.block_size]
            encrypted += self._encrypt_block(block)
        
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt(self, encryptedData: str) -> str:
        """
        解密
        Args:
            encryptedData：Blowfish密文
        Returns:
            明文
        """
        if not encryptedData:
            return ""
        data = base64.b64decode(encryptedData)
        
        # 分块解密
        decrypted = b''
        for i in range(0, len(data), self.block_size):
            block = data[i:i + self.block_size]
            decrypted += self._decrypt_block(block)
        
        # 去除PKCS7填充
        padding_len = decrypted[-1]
        if padding_len <= self.block_size:
            decrypted = decrypted[:-padding_len]
        
        return decrypted.decode('utf-8')
    