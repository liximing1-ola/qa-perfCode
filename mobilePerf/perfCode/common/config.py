#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试配置
"""
import random
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """性能测试配置类"""
    
    # 目标应用
    package: str = 'com.xx.xx.xxx'
    device_id: str = 'b286dc11'
    
    # 采集间隔（秒）
    period: int = 30
    
    # 网络类型
    network: str = "wifi"
    
    # Monkey 测试配置
    monkey_seed: str = field(default_factory=lambda: str(random.randrange(1, 10000)))
    monkey_params: str = (
        "--throttle 500 --ignore-crashes --ignore-timeouts "
        "--pct-touch 50 --pct-nav 20 --pct-appswitch 25 "
        "--pct-syskeys 5 --pct-motion 5 --pct-majornav 5 "
        "-v -v 10000"
    )
    
    # 日志路径
    log_dir: Path = field(default_factory=lambda: Path("E:/report/log"))
    
    @property
    def log_file(self) -> Path:
        """获取当前日志文件路径"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%d-%H-%M')
        return self.log_dir / f"{timestamp}-log.txt"
    
    def ensure_dirs(self) -> None:
        """确保所需目录存在"""
        self.log_dir.mkdir(parents=True, exist_ok=True)


# 全局配置实例
config = Config()
