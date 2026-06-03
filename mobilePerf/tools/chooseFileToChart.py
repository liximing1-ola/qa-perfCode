#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SoloPi 性能数据拉取和整理工具（手动选择文件夹）"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from solopi_utils import ADBError, run_adb, list_solopi_dirs, get_paths, pull_data, organize_files


def check_device() -> bool:
    """检查设备连接"""
    rc, stdout, stderr = run_adb(['adb', 'devices'])
    if rc != 0:
        raise ADBError(f'ADB 命令执行失败：{stderr}')

    if 'device' not in stdout:
        print('请检查设备 USB 连接')
        return False
    return True


def select_directory(dirs: list[str]) -> str | None:
    """交互式选择目录"""
    print('\n可用数据文件夹:')
    for i, d in enumerate(dirs, 1):
        print(f'  {i}. {d}')
    print('  0. 退出')

    choice = input('\n选择文件夹序号: ').strip()
    if choice == '0':
        return None

    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(dirs)):
            print('序号超出范围')
            return None
        return dirs[idx]
    except ValueError:
        print('无效输入')
        return None


def main() -> int:
    """主函数"""
    try:
        print(f'当前时间：{datetime.now():%Y-%m-%d %H:%M}\n')

        # 检查设备
        if not check_device():
            return 1

        # 获取目录列表
        dirs = list_solopi_dirs()
        if not dirs:
            print('未找到数据目录')
            return 1

        # 用户选择
        selected = select_directory(dirs)
        if not selected:
            return 0

        # 拉取和整理数据
        data_path, temp_path = get_paths()

        pull_data(selected, data_path, temp_path)
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
