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
    
    # 线程安全的退出信号（类级别共享）
    _exit_event: threading.Event = field(default_factory=threading.Event, init=False, repr=False)
    
    @classmethod
    def is_exit(cls) -> bool:
        """检查是否收到退出信号"""
        if not hasattr(cls, '_exit_event_inst'):
            cls._exit_event_inst = threading.Event()
        return cls._exit_event_inst.is_set()
    
    @classmethod
    def set_exit(cls) -> None:
        """设置退出信号"""
        if not hasattr(cls, '_exit_event_inst'):
            cls._exit_event_inst = threading.Event()
        cls._exit_event_inst.set()
    
    @classmethod
    def clear_exit(cls) -> None:
        """清除退出信号"""
        if not hasattr(cls, '_exit_event_inst'):
            cls._exit_event_inst = threading.Event()
        cls._exit_event_inst.clear()

