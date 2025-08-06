# -*- coding: utf-8 -*-
''' ************************************************************ 
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 07/02/2025 16:37:26
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 07/02/2025 16:39:32
### FilePath: //pycorelibs//utils//string.py
### Description: 
### 
### Copyright (c) 2025 by AI Lingues, All Rights Reserved. 
********************************************************** '''

import datetime
import secrets
import string

class UniCodeGenerator:
    """
    创建随机码，日期前缀 + 随机码

    可配置、使用 secrets 生成高强度随机码的编码生成类
                    | 场景             | 参数示例                                        |
                    | ---------------- | ---------------------------------------------- |
                    | 邀请码（短）      | `prefix_date=False, random_length=6`           |
                    | 订单号（当天唯一） | `prefix_date=True, random_length=4`            |
                    | URL 安全短码      | `charset=string.ascii_letters + string.digits` |
    """    
    def __init__(
        self,
        prefix_date: bool = True,
        random_length: int = 6,
        charset: str = string.ascii_uppercase + string.digits,  # Base36
        separator: str = '-'
    ):
        """
        构建UniCodeGenerator实例

        Args:
            prefix_date (bool, optional): 是否使用日期前缀. Defaults to True.
            random_length (int, optional): 随机码长度. Defaults to 6.
            charset (str, optional): 随机码字符集，默认使用 Base36. Defaults to string.ascii_uppercase+string.digits.
            separator (str,optional): 前缀和随机码之间的分隔符,缺省为'-'
            
        Returns:
            UniCodeGenerator实例
        """    
        self.prefix_date = prefix_date
        self.random_length = random_length
        self.charset = charset
        self.separator = separator

    def generate(self, date: datetime.date = None) -> str:
        """
        创建唯一短码
        
        Args:
            date (datetime.date, optional): 日期对象. Defaults to None.

        Returns:
            str: 唯一短码字符串
        """        
        if self.prefix_date:
            if date is None:
                date = datetime.date.today()
            prefix = date.strftime('%Y%m%d')
        else:
            prefix = None

        random_part = ''.join(secrets.choice(self.charset) for _ in range(self.random_length))
        
        return f"{prefix if prefix else ''}{self.separator if prefix else ''}{random_part}"
    
if __name__ == "__main__":
    ucg=UniCodeGenerator(prefix_date=False)
    i=8
    while i>=0:            
        code_str=ucg.generate()
        print(code_str)
        i -= 1