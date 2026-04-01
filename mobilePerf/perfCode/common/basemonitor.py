#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能监控器基类
定义性能数据采集的标准接口
"""
from abc import ABC, abstractmethod
from typing import Any


class Monitor(ABC):
    """性能监控器抽象基类
    
    子类需要实现 start, stop, save 方法
    """

    def __init__(self, **kwargs: Any):
        self.config = kwargs
        self.matched_data: dict = {}

    @abstractmethod
    def start(self) -> None:
        """开始采集性能数据"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """停止采集性能数据"""
        pass

    @abstractmethod
    def save(self) -> None:
        """保存采集的数据"""
        pass

    def clear(self) -> None:
        """清空已采集的数据"""
        self.matched_data.clear()

    def get_data(self) -> dict:
        """获取已采集的数据"""
        return self.matched_data.copy()
