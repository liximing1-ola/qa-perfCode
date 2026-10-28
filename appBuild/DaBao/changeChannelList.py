#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""渠道包批量打包工具"""
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"

# 渠道配置
CHANNEL_CONFIG = {
    'slp': ['gw', 'tt', 'vivo', 'huawei', 'xiaomi', 'rongyao'],
    'xsg': ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'rongyao'],
}
DEFAULT_CHANNELS = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'rongyao', 'tt']


def get_channels(app_name: str, config_file: Path | None = None) -> list[str]:
    """根据应用名称获取渠道列表
    
    :param app_name: 应用名称
    :param config_file: 可选的配置文件路径（JSON 格式）
    :return: 渠道列表
    """
    # 优先从配置文件读取
    if config_file and config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            for prefix, channels in config.items():
                if app_name.startswith(prefix):
                    return channels
            return config.get('default', DEFAULT_CHANNELS)
        except (json.JSONDecodeError, OSError) as e:
            print(f"警告：配置文件读取失败 ({e})，使用默认配置")
    
    # 使用内置配置
    for prefix, channels in CHANNEL_CONFIG.items():
        if app_name.startswith(prefix):
            return channels
    return DEFAULT_CHANNELS


def rename_apk(output_path: Path) -> int:
    """重命名 APK 文件，格式：appName_v1.0_channel_release.apk -> appName-channel-release.apk
    
    增强容错性：支持多种文件名格式
    """
    count = 0
    for apk_file in output_path.glob('*.apk'):
        parts = apk_file.stem.split('_')
        
        # 标准格式：4段 (appName_version_channel_release)
        if len(parts) == 4:
            app_name, _, channel, _ = parts
            new_name = f"{app_name}-{channel}-release.apk"
        # 简化格式：3段 (appName_channel_release)
        elif len(parts) == 3:
            app_name, channel, _ = parts
            new_name = f"{app_name}-{channel}-release.apk"
        else:
            print(f"跳过（文件名格式不匹配）：{apk_file.name}")
            continue

        new_path = apk_file.parent / new_name
        # 避免覆盖已存在的文件
        if new_path.exists():
            stem = new_path.stem
            suffix = new_path.suffix
            counter = 1
            while new_path.exists():
                new_path = new_path.parent / f"{stem}_{counter}{suffix}"
                counter += 1

        apk_file.rename(new_path)
        count += 1

    return count


def build_channels(apk_file: Path, channels: list[str], output_path: Path) -> int:
    """批量打包渠道包
    
    逐个显示打包进度与 walle 输出
    """
    output_path.mkdir(parents=True, exist_ok=True)
    total = len(channels)

    for i, channel in enumerate(channels, 1):
        print(f"[{i}/{total}] 正在打包渠道：{channel}")
        cmd = ["java", "-jar", WALLE_JAR, "batch", "-c", channel,
               str(apk_file), str(output_path)]
        try:
            # 合并标准错误后统一回显，避免输出交错
            result = subprocess.run(cmd, check=True, text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if result.stdout:
                print(result.stdout, end='')
        except subprocess.CalledProcessError as e:
            print(f"打包失败：{channel}")
            if e.stdout:
                print(f"错误信息：{e.stdout}")
            return e.returncode
        except FileNotFoundError:
            print(f"错误：找不到 Java 或 {WALLE_JAR}，请检查环境配置")
            return 1

    return 0


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='渠道包批量打包工具')
    parser.add_argument('apk', type=Path, help='APK 文件路径')
    parser.add_argument('app_name', help='应用名称')
    parser.add_argument('app_version', help='应用版本')
    parser.add_argument('-o', '--output', type=Path,
                        help='输出目录（默认：D:/Build/{app}_{version}_{date}）')
    parser.add_argument('-c', '--config', type=Path,
                        help='渠道配置文件路径（JSON 格式）')
    args = parser.parse_args()

    # 验证 APK 文件
    if not args.apk.exists():
        print(f"错误：APK 文件不存在：{args.apk}")
        return 1

    # 生成输出路径
    today = datetime.now().strftime('%Y-%m-%d')
    if args.output:
        output_path = args.output
    else:
        output_path = Path(f'D:/Build/{args.app_name}_{args.app_version}_{today}')

    # 获取渠道列表
    channels = get_channels(args.app_name, args.config)

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
