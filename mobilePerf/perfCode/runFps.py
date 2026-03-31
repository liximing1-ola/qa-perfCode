#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FPS 测试工具 - 自动滑动屏幕模拟用户操作
"""
import argparse
import random
import re
import subprocess
import sys
import time

# 滑动序列配置
SWIPE_SEQUENCES = [
    [
        'input swipe 100 550 100 100 50',
        'input swipe 200 600 200 200 100',
        'input swipe 500 500 200 200 100'
    ],
    [
        'input swipe 400 250 360 100 150',
        'input swipe 500 720 400 500 150'
    ]
]

DEVICE_PATTERN = re.compile(r'^(\S+)\s+device$', re.MULTILINE)
PACKAGE_PATTERN = re.compile(r'\((.*?)/', re.S)


def get_device() -> str | None:
    """获取第一个连接的设备 ID"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
        match = DEVICE_PATTERN.search(result.stdout)
        return match.group(1) if match else None
    except (subprocess.CalledProcessError, Exception) as e:
        print(f"获取设备失败: {e}")
        return None


def get_package_name(device: str, activity: str = 'com.x.x.android.MainActivity') -> str:
    """获取当前运行的应用包名"""
    try:
        cmd = f'adb -s {device} shell dumpsys window w | findstr / | findstr name='
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        for line in result.stdout.splitlines():
            if activity in line:
                match = PACKAGE_PATTERN.search(line)
                if match:
                    return match.group(1).split()[-1]
        
        return '未找到包名，请先启动应用'
    except Exception as e:
        return f'获取包名失败: {e}'


def run_swipe_test(device: str, count: int = 2000, batch_size: int = 20) -> None:
    """执行滑动测试"""
    print(f'开始 FPS 测试，设备: {device}')
    
    for i in range(1, count + 1):
        swipe_list = random.choice(SWIPE_SEQUENCES)
        swipe_cmd = random.choice(swipe_list)
        
        subprocess.run(['adb', '-s', device, 'shell', swipe_cmd], capture_output=True)
        
        if i % batch_size == 0:
            print(f'进度: {i}/{count}')
        
        time.sleep(0.05)
    
    print(f'测试完成，共执行 {count} 次滑动')


def main() -> int:
    parser = argparse.ArgumentParser(description='FPS 测试工具 - 自动滑动屏幕')
    parser.add_argument('-c', '--count', type=int, default=2000, help='滑动次数，默认 2000')
    parser.add_argument('-d', '--device', help='指定设备 ID，默认自动获取')
    parser.add_argument('--get-package', action='store_true', help='获取当前包名')
    args = parser.parse_args()

    device = args.device or get_device()
    if not device:
        print("错误: 未找到连接的设备")
        return 1

    print(f'设备: {device}')

    if args.get_package:
        package = get_package_name(device)
        print(f'包名: {package}')
        return 0

    run_swipe_test(device, args.count)
    return 0


if __name__ == '__main__':
    sys.exit(main())
