#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walle 渠道包打包工具

Usage:
  显示渠道: python batchChannelV2.py show <apk>
  单个渠道: python batchChannelV2.py <apk> <channel>
  多个渠道: python batchChannelV2.py <apk> <ch1,ch2,ch3>
  序号批量: python batchChannelV2.py <apk> <channel_prefix> <start> <end>
  配置文件: python batchChannelV2.py <apk> -f <config_file>
"""
import sys
import os
import subprocess
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"


def run_walle(*args) -> int:
    """执行 walle 命令"""
    cmd = ["java", "-jar", WALLE_JAR] + list(args)
    return subprocess.call(cmd)


def show_channel(apk_file: str) -> int:
    """显示 APK 渠道信息"""
    return run_walle("show", apk_file)


def generate_channel_names(channel_arg: str, seq_args: list = None) -> list:
    """生成渠道名称列表"""
    if not seq_args:
        return channel_arg.split(',')
    
    start, end = int(seq_args[0]), int(seq_args[1])
    width = len(str(end))
    return [f"{channel_arg}{i:0{width}d}" for i in range(start, end + 1)]


def rename_apk(apk_name: str, channel: str) -> None:
    """重命名生成的 APK 文件"""
    # 解析文件名: appName_channelName-version.apk -> appName-channelName-version.apk
    old_name = f"{apk_name}_{channel}.apk"
    parts = old_name.split('-')
    if len(parts) >= 2:
        parts[1] = channel
        parts[-1] = parts[-1].split('_')[0]
        new_name = '-'.join(parts)
        if Path(old_name).exists():
            os.rename(old_name, new_name)


def process_channels(apk_file: str, channel_arg: str, seq_args: list = None) -> int:
    """处理渠道包打包"""
    channel_names = generate_channel_names(channel_arg, seq_args)
    apk_name = Path(apk_file).stem
    
    for channel in channel_names:
        # 打包
        ret = run_walle("batch", "-c", channel, apk_file)
        if ret != 0:
            print(f"打包失败: {channel}")
            return ret
        # 重命名
        rename_apk(apk_name, channel)
    
    return 0


def process_config_file(apk_file: str, config_file: str) -> int:
    """从配置文件读取渠道列表"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                args = line.split()
                if len(args) >= 1:
                    ret = process_channels(apk_file, args[0], args[1:3])
                    if ret != 0:
                        return ret
        return 0
    except FileNotFoundError:
        print(f"配置文件不存在: {config_file}")
        return 1


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    # 显示渠道模式
    if sys.argv[1] == 'show' and len(sys.argv) >= 3:
        return show_channel(sys.argv[2])

    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    apk_file, channel_arg = sys.argv[1], sys.argv[2]

    # 配置文件模式
    if channel_arg == '-f' and len(sys.argv) >= 4:
        return process_config_file(apk_file, sys.argv[3])

    # 序号批量模式
    if len(sys.argv) >= 5:
        return process_channels(apk_file, channel_arg, sys.argv[3:5])

    # 单渠道或多渠道模式
    return process_channels(apk_file, channel_arg)


if __name__ == '__main__':
    sys.exit(main())
