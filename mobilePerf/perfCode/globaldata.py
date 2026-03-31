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
    """运行时数据类"""
    old_pid: int | None = None
    packages: list[str] | None = None
    package_save_path: str | None = None
    start_time: float | None = None
    top_dir: str | None = None
    config_dic: dict[str, Any] = field(default_factory=dict)
    _exit_event: threading.Event = field(default_factory=threading.Event)
    
    def is_exit(self) -> bool:
        """检查是否收到退出信号"""
        return self._exit_event.is_set()
    
    def set_exit(self) -> None:
        """设置退出信号"""
        self._exit_event.set()
    
    def clear_exit(self) -> None:
        """清除退出信号"""
        self._exit_event.clear()


# 全局实例
runtime = RuntimeData()
