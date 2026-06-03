#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SoloPi 数据采集共享配置"""

# SoloPi 设备端数据存储路径（相对路径）
SOLOPI_PATH = 'records/records/records'

# SoloPi 设备端数据根目录
ADB_REMOTE_BASE = '/storage/emulated/0/solopi/records'

# 数据类型映射：文件名前缀 -> (目标文件夹, 数据类型名称)
DATA_TYPES = {
    '帧率_FPS': ('FPS', 'FPS'),
    'PSS_main': ('MEM', 'MEM'),
    'process_main': ('CPU', 'CPU'),
    'CPU 温度_Temperature': ('TEMP', 'TEMP'),
}
