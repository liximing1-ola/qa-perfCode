#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoloPi 性能数据拉取和整理工具
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# 配置
SOLOPI_PATH = 'records/records/records'
DATA_TYPES = {
    '帧率_FPS': ('FPS', 'FPS'),
    'PSS_main': ('MEM', 'MEM'),
    'process_main': ('CPU', 'CPU'),
    'CPU温度_Temperature': ('TEMP', 'TEMP')
}


def get_project_paths() -> tuple[Path, Path]:
    """获取项目路径"""
    base_path = Path(__file__).parent.parent
    data_path = base_path / 'report'
    temp_path = data_path / 'prefData'
    return data_path, temp_path


def run_adb(cmd: str, timeout: int = 30) -> tuple[int, str, str]:
    """执行 ADB 命令"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        encoding='utf-8', timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_device() -> bool:
    """检查设备连接"""
    rc, stdout, _ = run_adb('adb devices')
    if rc != 0 or 'device' not in stdout:
        print('请检查设备 USB 连接')
        return False
    return True


def list_solopi_dirs() -> list[str]:
    """列出 SoloPi 数据目录"""
    cmd = f'adb shell ls /storage/emulated/0/solopi/records/{SOLOPI_PATH}'
    rc, stdout, stderr = run_adb(cmd)
    
    if rc != 0:
        print(f'无法访问 SoloPi 目录: {stderr}')
        return []
    
    # 过滤有效的目录名（29字符时间戳）
    return [d for d in stdout.split('\n') if len(d.strip()) == 29]


def pull_data(remote_dir: str, local_path: Path, temp_path: Path) -> bool:
    """拉取数据"""
    # 清理旧数据
    if temp_path.exists():
        shutil.rmtree(temp_path)
    
    # 拉取数据
    remote = f'/storage/emulated/0/solopi/records/{SOLOPI_PATH}/{remote_dir}'
    rc, _, stderr = run_adb(f'adb pull {remote} {local_path}')
    
    if rc != 0:
        print(f'拉取数据失败: {stderr}')
        return False
    
    # 重命名
    (local_path / remote_dir).rename(temp_path)
    return True


def organize_files(temp_path: Path, data_path: Path) -> None:
    """整理文件到对应目录"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for filename in temp_path.iterdir():
        if not filename.is_file():
            continue
        
        for prefix, (folder, name) in DATA_TYPES.items():
            if filename.name.startswith(prefix):
                dest_dir = data_path / folder
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / f'{name}_{today}.csv'
                shutil.move(str(filename), str(dest_file))
                print(f'{folder} 数据已保存')
                break


def main() -> int:
    print(f'当前时间: {datetime.now():%Y-%m-%d %H:%M}\n')
    
    # 检查设备
    if not check_device():
        return 1
    
    # 获取目录列表
    dirs = list_solopi_dirs()
    if not dirs:
        print('未找到数据目录')
        return 1
    
    print('可用数据文件夹:')
    for i, d in enumerate(dirs, 1):
        print(f'  {i}. {d}')
    
    # 用户选择
    choice = input('\n选择文件夹序号 (1=退出): ').strip()
    if choice == '1':
        return 0
    
    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(dirs)):
            raise ValueError
        selected = dirs[idx]
    except ValueError:
        print('无效输入')
        return 1
    
    # 拉取和整理数据
    data_path, temp_path = get_project_paths()
    
    if not pull_data(selected, data_path, temp_path):
        return 1
    
    organize_files(temp_path, data_path)
    
    print(f'\n完成！数据保存在: {data_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
