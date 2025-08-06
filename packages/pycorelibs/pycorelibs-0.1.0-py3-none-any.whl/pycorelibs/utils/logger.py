# -*- coding: utf-8 -*-
''' ************************************************************ 
### Author: Zeng Shengbo shengbo.zeng@ailingues.com
### Date: 2025-07-02 12:32:23
### LastEditors: Zeng Shengbo shengbo.zeng@ailingues.com
### LastEditTime: 2025-07-02 12:43:32
### FilePath: //pycorelibs//utils//logger.py
### Description: 日志，支持多颜色和进度条
###              全局仅有一个日志，同时向控制台和日志文件输出日志    
### Copyright (c) 2025 by AI Lingues, All Rights Reserved. 
********************************************************** '''
from pathlib import Path
from datetime import datetime as dt
import logging
import threading
from rich.logging import RichHandler
from rich.console import Console


class FileLoggingConsole(Console):
    def __init__(self, log_file_path, *args, **kwargs):
        """
        自定义 Console，既会在控制台输出信息，也会将输出内容写入同一个日志文件。
        """
        super().__init__(*args, **kwargs)
        # 确保是字符串路径（如果 CFG_APP_LOG_FILE 是 Path 对象）
        self.log_file_path = str(log_file_path)
        # 用 append 模式打开同一个日志文件
        self.log_file = open(self.log_file_path, "a", encoding="utf-8")
        # 如果有多线程写日志，使用锁保证写文件和 print 的原子性
        self._write_lock = threading.Lock()

    def print(self, *args, **kwargs):
        """
        重载 print 方法，输出到控制台后再写入日志文件。
        """
        with self._write_lock:
            # 先调用原始 Console 的 print 方法，让 Rich 先输出到控制台
            super().print(*args, **kwargs)
            # 将本次所有待输出的文本用 export_text() 导出，并写入日志文件
            text = self.export_text()
            self.log_file.write(text+'\n')
            self.log_file.flush()

    def __del__(self):
        """
        在对象销毁前，记得关闭文件句柄。
        """
        if hasattr(self, "log_file") and self.log_file:
            self.log_file.close()


class Logger:
    _instance = None

    def __new__(cls, log_dir: str = "./logs", *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            log_root = Path(log_dir)
            if not log_root.exists():
                log_root.mkdir(exist_ok=True)
            cls._instance._init_logger(Path(log_dir))
        return cls._instance

    def _init_logger(self, log_root: Path):
        # 创建自定义 Console（在控制台打印的同时写入同一个日志文件）
        formatted_time = dt.now().strftime("%Y%m%d_%H%M%S")
        log_file_path = log_root / f"{formatted_time}.log"
        self.console = FileLoggingConsole(log_file_path=log_file_path, record=True)

        # 配置 RichHandler，用上面创建的 console 作为输出
        rich_handler = RichHandler(
            console=self.console,
            rich_tracebacks=True,  # 启用丰富的错误堆栈
            show_path=False,  # 隐藏日志中路径信息
        )

        # 创建日志记录器，并添加 RichHandler
        self.logger = logging.getLogger("GlobalLogger")
        self.logger.setLevel(logging.DEBUG)  # 可以根据需要调整
        self.logger.addHandler(rich_handler)

        # 注意：不要再单独添加另外的 FileHandler，
        #       否则会和 FileLoggingConsole 争用同一个日志文件

    def get_logger(self):
        return self.logger

    def get_console(self):
        return self.console

