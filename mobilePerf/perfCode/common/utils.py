#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
"""
import os
import time
import re
import zipfile
from datetime import datetime
from pathlib import Path


def ms2s(value: float) -> float:
    """毫秒转秒"""
    return round(value / 1000.0, 2)


def transfer_temp(temp: float) -> float:
    """温度转换"""
    return round(temp / 10.0, 1)


def mV2V(v: float) -> float:
    """毫伏转伏"""
    return round(v / 1000.0, 2)


def uA2mA(c: float) -> float:
    """微安转毫安"""
    return round(c / 1000.0, 2)


class TimeUtils:
    """时间工具类"""
    UNDERLINE_FMT = "%Y_%m_%d_%H_%M_%S"
    NORMAL_FMT = "%Y-%m-%d %H-%M-%S"
    COLON_FMT = "%Y-%m-%d %H:%M:%S"

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

    @staticmethod
    def is_between(timestamp: float, begin: float, end: float) -> bool:
        """判断时间是否在范围内"""
        return begin < timestamp < end

    @staticmethod
    def get_hours_diff(begin: float, end: float) -> int:
        """获取时间差（小时）"""
        return round((end - begin) / 3600)


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def ensure_dir(path: str | Path) -> Path:
        """确保目录存在，返回 Path 对象"""
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @staticmethod
    def get_project_root() -> Path:
        """获取项目根目录"""
        return Path(__file__).parent.parent.parent

    @staticmethod
    def find_files(directory: str | Path, pattern: str | None = None) -> list[Path]:
        """递归查找文件"""
        path = Path(directory)
        if not path.exists():
            return []
        
        files = []
        regex = re.compile(pattern) if pattern else None
        
        for item in path.rglob('*'):
            if item.is_file():
                if regex is None or regex.match(item.name):
                    files.append(item)
        
        return files

    @staticmethod
    def get_file_size_mb(filepath: str | Path) -> float:
        """获取文件大小（MB）"""
        return round(Path(filepath).stat().st_size / (1024 * 1024), 4)


class ZipUtils:
    """压缩工具类"""
    
    @staticmethod
    def zip_directory(source_dir: str | Path, output_zip: str | Path) -> None:
        """压缩目录"""
        source = Path(source_dir)
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in source.rglob('*'):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(source))
                    zf.write(file_path, arcname)


if __name__ == '__main__':
    # 测试
    print(f"当前时间: {TimeUtils.get_current_time()}")
    print(f"项目根目录: {FileUtils.get_project_root()}")
