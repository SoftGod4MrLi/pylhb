"""
模块：myfile
作者：李生
描述：文件操作
"""
import json
import csv

class MyFile:
    """文件管理类"""
    def saveDataDictionaryList2JSON(data,fileName) -> tuple[bool,str]:
        """
        数据字典列表保存为JSON文件
        Args:
            data：MyMSSQL读取数据库得到的数据字典
            fileName：JSON文件名
        Returns:
            是否成功，执行结果
        """
        if not data:
            return False,"数据无效。"
        try:
            with open(fileName, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return True,"OK"
        except Exception as e:
            return False,f"{e}"
        
    def saveDataDictionaryList2CSV(data,fileName) -> tuple[bool,str]:
        """
        数据字典列表保存为CSV文件
        Args:
            data：MyMSSQL读取数据库得到的数据字典
            fileName：CSV文件名
        Returns:
            是否成功，执行结果
        """
        if not data:
            return False,"数据无效。"
        try:
            # 获取所有键名（列名）
            fieldnames = data[0].keys()
            with open(fileName, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True,"OK"
        except Exception as e:
            return False,f"{e}"
            
    def readDataDictionaryListFromJSON(fileName):
        """
        从JSON读取数据字典列表
        Args:
            fileName：JSON文件名
        Returns:
            数据字典列表
        """
        try:
            with open(fileName, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            return None
    
    def readDataDictionaryListFromCSV(fileName):
        """
        从CSV读取数据字典列表
        Args:
            fileName：CSV文件名
        Returns:
            数据字典列表
        """
        try:
            data = []
            with open(fileName, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            return data
        except Exception as e:
            return None
        
    def splitFile(fileName, chunkSize = 20 * 1024 * 1024):
        """
        拆发文件
        Args:
            fileName：拆分文件名
            chunkSize：拆分大小
        Returns:
            是否成功，文件个数，文件列表
        """
        try:
            splitedFiles=[]
            with open(fileName, 'rb') as f:
                part_num = 0
                while True:
                    chunk = f.read(chunkSize)
                    if not chunk:
                        break
                    part_num += 1
                    splitFile=f"{fileName}.part{part_num}"
                    with open(splitFile, 'wb') as chunk_file:
                        chunk_file.write(chunk)
                    splitedFiles.append(splitFile)
            return True, part_num, splitedFiles
        except Exception as e:
            return False,0,None
    
    def mergeFiles(splitedFiles, mergeToFile) -> bool:
        """
        合并文件
        Args:
            splitedFiles：需要合并的那些拆分文件
            mergeToFile：合并的文件名
        Returns:
            是否成功
        """
        try:
            with open(mergeToFile, 'wb') as outfile:
                for file in splitedFiles:
                    with open(file, 'rb') as infile:
                        while chunk := infile.read():
                            outfile.write(chunk)
            return True
        except Exception as e:
            return False
        