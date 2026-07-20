#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行时全局数据共享模块
"""
import threading
from dataclasses import dataclass, field
from typing import Any


@dataclass
class RuntimeData:
    """运行时全局数据类
    
    注意：本类作为全局状态容器直接使用类属性，不需要实例化。
    例如：RuntimeData.package_save_path = '/path/to/dir'
    """
    old_pid: int | None = None
    packages: list[str] | None = None
    package_save_path: str | None = None
    start_time: float | None = None
    top_dir: str | None = None
    config_dic: dict[str, Any] = field(default_factory=dict)
    
    # 线程安全的退出信号（类级别共享，所有实例共用同一个 Event）
    _exit_signal: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
    
    @classmethod
    def is_exit(cls) -> bool:
        """检查是否收到退出信号"""
        return cls._exit_signal.is_set()
    
    @classmethod
    def set_exit(cls) -> None:
        """设置退出信号"""
        cls._exit_signal.set()
    
    @classmethod
    def clear_exit(cls) -> None:
        """清除退出信号"""
        cls._exit_signal.clear()

