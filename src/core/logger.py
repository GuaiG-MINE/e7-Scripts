#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : logger.py
@Author  : Guaig
@Date    : 2026-06-25
@Desc    : logger.py - 全局日志管理器，支持日志文件自动清理、异常捕获与格式化输出
"""

import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

class AppLogger:
    def __init__(self, log_dir="logs", keep_logs=100):
        # 1. 确保日志目录存在
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # 🌟 2. 自动清理旧日志（只保留最近的 keep_logs 个）
        self._cleanup_old_logs(keep=keep_logs)
        
        # 🌟 3. 精确到秒的文件名，每次运行独立一个文件
        # 例如: app_2026-06-25_09-30-35.log
        time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.log_file = self.log_dir / f"app_{time_str}.log"
        
        # 4. 配置 Logger
        self.logger = logging.getLogger("GameBot")
        self.logger.setLevel(logging.DEBUG)
        
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                fmt='[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
        # 接管全局未捕获的异常
        sys.excepthook = self._handle_unhandled_exception
        
        # 每次启动时，在日志开头打个招呼，方便确认启动时间
        self.logger.info("="*40)
        self.logger.info(f"🚀 程序全新启动 | 记录时间: {time_str}")
        self.logger.info("="*40)

    def _cleanup_old_logs(self, keep=10):
        """清理旧日志文件，防止占用过多硬盘空间"""
        try:
            # 找到所有 app_ 开头的 log 文件
            log_files = list(self.log_dir.glob("app_*.log"))
            # 按文件的修改时间排序（旧的在前，新的在后）
            log_files.sort(key=lambda f: f.stat().st_mtime)
            
            # 如果文件数量超过了保留数量，就把最旧的删掉
            if len(log_files) > keep:
                files_to_delete = log_files[:-keep]
                for f in files_to_delete:
                    f.unlink(missing_ok=True)
        except Exception as e:
            print(f"清理旧日志失败: {e}")

    def _handle_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        self.logger.critical(
            "❌ 程序发生未捕获的崩溃 (Unhandled Exception):", 
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    # 快捷方法
    def info(self, msg): self.logger.info(msg)
    def error(self, msg, exc_info=False): self.logger.error(msg, exc_info=exc_info)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)

log_manager = AppLogger()
