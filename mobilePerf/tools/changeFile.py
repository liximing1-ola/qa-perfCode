#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SoloPi 性能数据自动拉取工具（自动获取最新文件夹）"""
import subprocess
import sys
from datetime import datetime

from solopi_utils import ADBError, get_latest_folder, get_paths, pull_data, organize_files


def main() -> int:
    """主函数"""
    try:
        print(f'当前时间：{datetime.now():%Y-%m-%d %H:%M}\n')

        # 获取最新文件夹
        latest = get_latest_folder()
        if not latest:
            print('未找到数据文件夹')
            return 1

        print(f'自动获取最新文件夹：{latest}\n')

        # 拉取和整理
        data_path, temp_path = get_paths()

        if not pull_data(latest, data_path, temp_path):
            return 1

        count = organize_files(temp_path, data_path)

        print(f'\n完成！共处理 {count} 个文件')
        print(f'数据保存在：{data_path}')
        return 0

    except ADBError as e:
        print(f'ADB 错误：{e}')
        return 1
    except subprocess.TimeoutExpired:
        print('ADB 命令超时，请检查设备连接')
        return 1
    except Exception as e:
        print(f'未知错误：{e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
