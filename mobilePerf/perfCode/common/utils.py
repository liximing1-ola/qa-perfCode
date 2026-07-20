#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
"""
from datetime import datetime


def ms2s(value: float) -> float:
    """毫秒转秒"""
    return round(value / 1000.0, 2)


class TimeUtils:
    """时间工具类"""
    UNDERLINE_FMT = "%Y_%m_%d_%H_%M_%S"
    NORMAL_FMT = "%Y-%m-%d %H-%M-%S"

    @staticmethod
    def get_current_time_underline() -> str:
        """获取带下划线的时间字符串"""
        return datetime.now().strftime(TimeUtils.UNDERLINE_FMT)

    @staticmethod
    def get_current_time() -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime(TimeUtils.NORMAL_FMT)

    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """格式化时间戳"""
        return datetime.fromtimestamp(timestamp).strftime(TimeUtils.NORMAL_FMT)

    @staticmethod
    def parse_time(time_str: str, fmt: str) -> float:
        """解析时间字符串为时间戳"""
        return datetime.strptime(time_str, fmt).timestamp()


if __name__ == '__main__':
    print(f"当前时间: {TimeUtils.get_current_time()}")
