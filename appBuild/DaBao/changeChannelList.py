#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渠道包批量打包工具
Usage: python changeChannelList.py <apkPath> <apkName> <appVersion> <CPU>
"""
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"

# 渠道配置
CHANNEL_CONFIG = {
    'slp': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'baidu'],
    'rbp': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb']
}
DEFAULT_CHANNELS = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'rongyao']


def get_channels(app_name: str) -> list:
    """根据应用名称获取渠道列表"""
    for prefix, channels in CHANNEL_CONFIG.items():
        if app_name.startswith(prefix):
            return channels
    return DEFAULT_CHANNELS


def rename_apk(path: str, app_so: str) -> None:
    """重命名 APK 文件"""
    for app in os.listdir(path):
        if not app.endswith('.apk'):
            continue
        
        # 解析文件名: appName_v1.0_channel_release.apk
        parts = app[:-4].split('-')
        if len(parts) < 2:
            continue
        
        channel = parts[-1].split('_')[1] if '_' in parts[-1] else parts[-1]
        new_name = f"{parts[0]}-{channel}-release-{app_so}.apk"
        
        old_path = Path(path) / app
        new_path = Path(path) / new_name
        old_path.rename(new_path)


def build_channels(apk_file: str, channels: list, output_path: str) -> int:
    """批量打包渠道包"""
    Path(output_path).mkdir(parents=True, exist_ok=True)
    
    for channel in channels:
        cmd = ["java", "-jar", WALLE_JAR, "batch", "-c", channel, apk_file, output_path]
        ret = subprocess.call(cmd)
        if ret != 0:
            print(f"打包失败: {channel}")
            return ret
    
    return 0


def main() -> int:
    if len(sys.argv) != 5:
        print(__doc__)
        return 1

    apk_file, app_name, app_version, app_so = sys.argv[1:5]
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = f'D:/Build/{app_name}_{app_version}_{app_so}_{today}'

    channels = get_channels(app_name)
    
    print(f"开始打包: {app_name}")
    print(f"渠道列表: {channels}")
    
    ret = build_channels(apk_file, channels, output_path)
    if ret != 0:
        return ret

    rename_apk(output_path, app_so)
    
    print(f"\n打包完成: {output_path}")
    print(f"生成文件: {os.listdir(output_path)}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
