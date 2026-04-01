#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置模块
"""
import logging
import logging.handlers
import os
import re
import sys
from pathlib import Path


def get_log_dir() -> str:
    """获取日志目录路径"""
    # 从当前文件向上回溯到项目根目录
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[2]  # common -> perfCode -> mobilePerf
    return str(project_root / 'logs')


def create_logger(
    name: str = 'mobileperf',
    log_level: int = logging.DEBUG,
    console_level: int = logging.INFO,
    log_dir: str = None
) -> logging.Logger:
    """
    创建并配置日志记录器
    
    :param name: 日志记录器名称
    :param log_level: 日志文件记录级别
    :param console_level: 控制台输出级别
    :param log_dir: 日志目录，默认自动获取
    :return: 配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s]%(levelname)s:%(name)s:%(module)s:%(message)s'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(console_level)
    logger.addHandler(console_handler)
    
    # 文件处理器
    if log_dir is None:
        log_dir = get_log_dir()
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    log_file = Path(log_dir) / "xn_log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when="D",
        interval=1,
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\.log$")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    logger.addHandler(file_handler)
    
    return logger


# 默认日志记录器
logger = create_logger()


if __name__ == "__main__":
    logger.debug("debug test")
    logger.info("info test")
    logger.warning("warning test")
    logger.error("error test")
