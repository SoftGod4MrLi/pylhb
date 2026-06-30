"""
模块：mydownload
作者：李生
描述：文件下载
"""
import urllib.request
import os
import sys

class MyDownload:
    """文件下载类"""
    def downloadFile(self, url, savePath=None, showProgress = True):
        """
        下载文件并显示进度条
        Args:
            url: 文件的URL地址
            savePath: 保存路径，如果不指定则使用URL中的文件名
        Returns: 
            实际保存的文件路径
        """
        def show_progress(current, total, width=50):
            """显示进度条"""
            if total > 0:
                percent = current / total
                filled = int(width * percent)
                bar = '=' * filled + '>' + '.' * (width - filled - 1)
                sys.stdout.write(f'\r[{bar}] {percent:.1%} ({current}/{total} bytes)')
                sys.stdout.flush()
        # 如果没有指定保存路径，从URL中提取文件名
        if savePath is None:
            savePath = url.split('/')[-1]
            if not savePath:  # 如果URL以/结尾
                savePath = 'downloaded_file'
        # 创建临时文件名（下载完成后重命名）
        temp_path = savePath + '.tmp'
        try:
            # 发送HTTP请求
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            with urllib.request.urlopen(req) as response:
                # 获取文件大小
                total_size = response.headers.get('Content-Length')
                if total_size is not None:
                    total_size = int(total_size)
                else:
                    total_size = 0
                # 打开临时文件准备写入
                with open(temp_path, 'wb') as file:
                    downloaded = 0
                    chunk_size = 8192  # 每次读取8KB
                    
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        file.write(chunk)
                        downloaded += len(chunk)
                        # 更新进度条
                        if showProgress:
                            if total_size > 0:
                                show_progress(downloaded, total_size)
                            else:
                                # 如果不知道总大小，只显示已下载大小
                                sys.stdout.write(f'\r已下载: {downloaded/1024/1024:.2f} MB')
                                sys.stdout.flush()
            # 下载完成后重命名临时文件
            if os.path.exists(savePath):
                os.remove(savePath)  # 如果文件已存在，删除
            os.rename(temp_path, savePath)
            return savePath
        except Exception as e:
            # 发生错误时清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise Exception(f"下载失败: {str(e)}")
            