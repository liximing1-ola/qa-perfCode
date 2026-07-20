#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渠道包批量打包工具"""
import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"

# 渠道配置
CHANNEL_CONFIG = {
    'slp': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'rongyao'],
    'xsg': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'rongyao'],
}
DEFAULT_CHANNELS = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'rongyao']


def get_channels(app_name: str) -> list[str]:
    """根据应用名称获取渠道列表"""
    for prefix, channels in CHANNEL_CONFIG.items():
        if app_name.startswith(prefix):
            return channels
    return DEFAULT_CHANNELS


def rename_apk(output_path: Path) -> int:
    """重命名 APK 文件，格式：appName_v1.0_channel_release.apk -> appName-channel-release.apk"""
    count = 0
    for apk_file in output_path.glob('*.apk'):
        parts = apk_file.stem.split('_')
        if len(parts) != 4:
            print(f"跳过（文件名格式不匹配）：{apk_file.name}")
            continue

        app_name, _, channel, _ = parts
        new_name = f"{app_name}-{channel}-release.apk"

        apk_file.rename(apk_file.parent / new_name)
        count += 1

    return count


def build_channels(apk_file: Path, channels: list[str], output_path: Path) -> int:
    """批量打包渠道包"""
    output_path.mkdir(parents=True, exist_ok=True)

    for channel in channels:
        cmd = ["java", "-jar", WALLE_JAR, "batch", "-c", channel,
               str(apk_file), str(output_path)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"打包失败：{channel}")
            print(f"错误信息：{e.stderr}")
            return e.returncode

    return 0


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='渠道包批量打包工具')
    parser.add_argument('apk', type=Path, help='APK 文件路径')
    parser.add_argument('app_name', help='应用名称')
    parser.add_argument('app_version', help='应用版本')
    parser.add_argument('-o', '--output', type=Path,
                        help='输出目录（默认：D:/Build/{app}_{version}_{date}）')
    args = parser.parse_args()

    # 生成输出路径
    today = datetime.now().strftime('%Y-%m-%d')
    if args.output:
        output_path = args.output
    else:
        output_path = Path(f'D:/Build/{args.app_name}_{args.app_version}_{today}')

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
    renamed = rename_apk(output_path)
    print(f"\n重命名 {renamed} 个文件")

    print(f"\n打包完成：{output_path}")
    print(f"生成文件：{len(list(output_path.glob('*.apk')))} 个")
    return 0


if __name__ == '__main__':
    sys.exit(main())
