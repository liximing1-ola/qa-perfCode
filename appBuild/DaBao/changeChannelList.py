#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
渠道包批量打包工具

根据应用名称自动选择渠道列表，批量生成多渠道包
"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"

# 渠道配置
CHANNEL_CONFIG = {
    'slp': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'baidu'],
    'rbp': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb']
}
DEFAULT_CHANNELS = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'rongyao']


def get_channels(app_name: str) -> list[str]:
    """根据应用名称获取渠道列表
    
    :param app_name: 应用名称
    :return: 渠道列表
    """
    for prefix, channels in CHANNEL_CONFIG.items():
        if app_name.startswith(prefix):
            return channels
    return DEFAULT_CHANNELS


def rename_apk(output_path: Path, app_so: str) -> None:
    """重命名 APK 文件
    
    格式转换：appName_v1.0_channel_release.apk -> appName-channel-release-app_so.apk
    
    :param output_path: 输出目录
    :param app_so: 应用标识
    """
    for apk_file in output_path.glob('*.apk'):
        # 解析文件名
        parts = apk_file.stem.split('-')
        if len(parts) < 2:
            continue
        
        # 提取渠道名
        channel = parts[-1].split('_')[1] if '_' in parts[-1] else parts[-1]
        new_name = f"{parts[0]}-{channel}-release-{app_so}.apk"
        
        apk_file.rename(apk_file.parent / new_name)


def build_channels(apk_file: Path, channels: list[str], output_path: Path) -> int:
    """批量打包渠道包
    
    :param apk_file: APK 文件路径
    :param channels: 渠道列表
    :param output_path: 输出目录
    :return: 返回码
    """
    output_path.mkdir(parents=True, exist_ok=True)
    
    for channel in channels:
        cmd = ["java", "-jar", WALLE_JAR, "batch", "-c", channel, str(apk_file), str(output_path)]
        ret = subprocess.call(cmd)
        if ret != 0:
            print(f"打包失败：{channel}")
            return ret
    
    return 0


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='渠道包批量打包工具')
    parser.add_argument('apk', type=Path, help='APK 文件路径')
    parser.add_argument('app_name', help='应用名称')
    parser.add_argument('app_version', help='应用版本')
    parser.add_argument('app_so', help='应用标识（如 slp, rbp）')
    args = parser.parse_args()
    
    # 生成输出路径
    today = datetime.now().strftime('%Y-%m-%d')
    output_path = Path(f'D:/Build/{args.app_name}_{args.app_version}_{args.app_so}_{today}')
    
    # 获取渠道列表
    channels = get_channels(args.app_name)
    
    print(f"\n开始打包：{args.app_name}")
    print(f"渠道列表：{channels}")
    print(f"输出目录：{output_path}\n")
    
    # 批量打包
    ret = build_channels(args.apk, channels, output_path)
    if ret != 0:
        return ret
    
    # 重命名
    rename_apk(output_path, args.app_so)
    
    print(f"\n打包完成：{output_path}")
    print(f"生成文件：{len(list(output_path.glob('*.apk')))} 个")
    return 0


if __name__ == '__main__':
    sys.exit(main())
