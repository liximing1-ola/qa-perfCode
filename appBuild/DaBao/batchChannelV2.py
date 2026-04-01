#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Walle 渠道包打包工具

支持多种渠道打包模式：
- 显示渠道信息
- 单渠道打包
- 多渠道批量打包
- 序号范围批量打包
- 配置文件读取渠道列表
"""
import argparse
import subprocess
import sys
from pathlib import Path

WALLE_JAR = "walle-cli-all.jar"


def run_walle(*args) -> int:
    """执行 walle 命令"""
    cmd = ["java", "-jar", WALLE_JAR] + list(args)
    return subprocess.call(cmd)


def show_channel(apk_file: str) -> int:
    """显示 APK 渠道信息"""
    return run_walle("show", apk_file)


def generate_channel_names(channel_arg: str, seq_args: tuple[int, int] | None = None) -> list[str]:
    """生成渠道名称列表
    
    :param channel_arg: 渠道前缀或逗号分隔的渠道列表
    :param seq_args: 序号范围 (start, end)
    :return: 渠道名称列表
    """
    if not seq_args:
        return channel_arg.split(',')
    
    start, end = seq_args
    width = len(str(end))
    return [f"{channel_arg}{i:0{width}d}" for i in range(start, end + 1)]


def rename_apk(apk_name: str, channel: str) -> None:
    """重命名生成的 APK 文件
    
    格式转换：appName_channelName-version.apk -> appName-channelName-version.apk
    """
    old_name = f"{apk_name}_{channel}.apk"
    if not Path(old_name).exists():
        return
    
    parts = old_name.split('-')
    if len(parts) >= 2:
        parts[1] = channel
        parts[-1] = parts[-1].split('_')[0]
        new_name = '-'.join(parts)
        Path(old_name).rename(new_name)


def process_channels(apk_file: str, channel_arg: str, seq_args: tuple[int, int] | None = None) -> int:
    """处理渠道包打包
    
    :param apk_file: APK 文件路径
    :param channel_arg: 渠道参数
    :param seq_args: 序号范围
    :return: 返回码
    """
    channel_names = generate_channel_names(channel_arg, seq_args)
    apk_name = Path(apk_file).stem
    
    for channel in channel_names:
        # 打包
        ret = run_walle("batch", "-c", channel, apk_file)
        if ret != 0:
            print(f"打包失败：{channel}")
            return ret
        # 重命名
        rename_apk(apk_name, channel)
    
    return 0


def process_config_file(apk_file: str, config_file: str) -> int:
    """从配置文件读取渠道列表
    
    :param apk_file: APK 文件路径
    :param config_file: 配置文件路径
    :return: 返回码
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                args = line.split()
                if len(args) >= 1:
                    ret = process_channels(apk_file, args[0], tuple(map(int, args[1:3])) if len(args) >= 3 else None)
                    if ret != 0:
                        return ret
        return 0
    except FileNotFoundError:
        print(f"配置文件不存在：{config_file}")
        return 1
    except ValueError as e:
        print(f"配置文件解析错误：{e}")
        return 1


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Walle 渠道包打包工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 显示渠道信息
  python batchChannelV2.py show app.apk
  
  # 单渠道打包
  python batchChannelV2.py app.apk xiaomi
  
  # 多渠道批量打包
  python batchChannelV2.py app.apk huawei,oppo,vivo
  
  # 序号范围批量打包
  python batchChannelV2.py app.apk channel_ 1 100
  
  # 使用配置文件
  python batchChannelV2.py app.apk -f channels.txt
        """
    )
    
    parser.add_argument('apk', help='APK 文件路径')
    parser.add_argument('channel', nargs='?', help='渠道名称、逗号分隔的渠道列表或渠道前缀')
    parser.add_argument('start', type=int, nargs='?', help='序号范围起始值')
    parser.add_argument('end', type=int, nargs='?', help='序号范围结束值')
    parser.add_argument('-f', '--file', dest='config_file', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 显示渠道模式
    if args.channel == 'show':
        return show_channel(args.apk)
    
    # 配置文件模式
    if args.config_file:
        return process_config_file(args.apk, args.config_file)
    
    # 检查必要参数
    if not args.channel:
        parser.print_help()
        return 1
    
    # 序号范围模式
    if args.start is not None and args.end is not None:
        return process_channels(args.apk, args.channel, (args.start, args.end))
    
    # 单渠道或多渠道模式
    return process_channels(args.apk, args.channel)


if __name__ == '__main__':
    sys.exit(main())
