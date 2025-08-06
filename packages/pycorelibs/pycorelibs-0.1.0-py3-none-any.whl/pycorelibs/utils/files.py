# -*- coding: utf-8 -*-
''' ************************************************************ 
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 07/03/2025 10:16:08
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 07/03/2025 10:37:12
### FilePath: //pycorelibs//utils//files.py
### Description: 文件对象有关的一些工具函数
### 
### Copyright (c) 2025 by AI Lingues, All Rights Reserved. 
********************************************************** '''

from pathlib import Path
import subprocess
import platform
from enum import Enum


class FileSizeUnit(Enum):
    BYTES = "B"
    KILOBYTES = "KB"
    MEGABYTES = "MB"
    GIGABYTES = "GB"
    TERABYTES = "TB"


def get_file_size(file_name: str, unit: FileSizeUnit = FileSizeUnit.BYTES) -> float:
    """
    获取文件大小，并返回指定单位的大小。

    支持B,KB,MB,GB,TB

    Args:
        file_name (str): 文件名(含路径)
        unit (FileSizeUnit, optional): 返回的大小单位，默认为字节（SizeUnit.BYTES）. Defaults to FileSizeUnit.BYTES.

    Raises:
        FileNotFoundError: 指定的文件不存在
        ValueError: 文件尺寸单位错误

    Returns:
        float: 文件大小，转换为指定单位
    """ 
    if not Path(file_name).exists():
        raise FileNotFoundError(f"The file '{file_name}' does not exist.")

    # 获取文件大小，单位为字节
    file_size_in_bytes = Path(file_name).stat().st_size

    # 转换大小到指定单位
    match unit:
        case FileSizeUnit.BYTES:
            return file_size_in_bytes
        case FileSizeUnit.KILOBYTES:
            return round(file_size_in_bytes / 1024, 2)
        case FileSizeUnit.MEGABYTES:
            return round(file_size_in_bytes / (1024**2), 2)
        case FileSizeUnit.GIGABYTES:
            return round(file_size_in_bytes / (1024**3), 2)
        case FileSizeUnit.TERABYTES:
            return round(file_size_in_bytes / (1024**4), 2)
        case _:
            raise ValueError(f"Unsupported size unit: {unit}")


def line_count(file_name: str)-> int:
    """
    获取指定文件的总行数

    Windows系统: 使用换行符作为判断标记
    Linux系统: 使用系统自带的wc命令统计
    
    注: 近适用于文本类型文件,其他类型如二进制文件统计结果不具备参考意义

    Args:
        file_name (str): 文件名(含路径)

    Raises:
        FileNotFoundError: 指定文件未能找到

    Returns:
        int: 统计的总行数
    """
    if not Path(file_name).exists():
        raise FileNotFoundError(f"The file '{file_name}' does not exist.")
    
    current_os = platform.system()
    if current_os == "Windows":
        from itertools import takewhile, repeat

        buffer = 1024 * 1024
        with open(file_name) as f:
            buf_gen = takewhile(lambda x: x, (f.read(buffer) for _ in repeat(None)))
            return sum(buf.count("\n") for buf in buf_gen)
    if current_os == "Linux":
        result = subprocess.run(["wc", "-l", file_name], capture_output=True, text=True)
        lc = int(result.stdout.split()[0])
        return lc
    return None
