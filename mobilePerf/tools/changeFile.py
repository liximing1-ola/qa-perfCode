#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoloPi 性能数据自动拉取工具（默认获取最新文件夹）
"""
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
SOLOPI_PATH = 'records/records/records'
DATA_TYPES = {
    '帧率_FPS': ('FPS', 'FPS'),
    'PSS-main': ('MEM', 'MEM'),
    '应用进程-main': ('CPU', 'CPU'),
    'CPU温度_Temperature': ('TEMP', 'TEMP')
}


def get_paths() -> tuple[Path, Path]:
    """获取项目路径"""
    base = Path(__file__).parent.parent
    data_path = base / 'report'
    return data_path, data_path / 'prefData'


def run_adb(cmd: str) -> tuple[int, str, str]:
    """执行 ADB 命令"""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, encoding='utf-8'
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_latest_folder() -> str | None:
    """获取 SoloPi 最新的数据文件夹"""
    cmd = f'adb shell ls /storage/emulated/0/solopi/records/{SOLOPI_PATH}'
    rc, stdout, stderr = run_adb(cmd)
    
    if rc != 0:
        print(f'请检查设备连接或 SoloPi 目录: {stderr}')
        return None
    
    # 获取有效的目录名（29字符时间戳）并返回最新的
    dirs = [d.strip() for d in stdout.split('\n') if len(d.strip()) == 29]
    return dirs[-1] if dirs else None


def pull_data(remote_dir: str, data_path: Path, temp_path: Path) -> bool:
    """拉取数据到本地"""
    # 清理旧数据
    if temp_path.exists():
        shutil.rmtree(temp_path)
    
    # 拉取
    remote = f'/storage/emulated/0/solopi/records/{SOLOPI_PATH}/{remote_dir}'
    rc, _, stderr = run_adb(f'adb pull {remote} {data_path}')
    
    if rc != 0:
        print(f'拉取失败: {stderr}')
        return False
    
    # 重命名为临时目录
    (data_path / remote_dir).rename(temp_path)
    return True


def organize_files(temp_path: Path, data_path: Path) -> None:
    """整理文件到对应目录"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    for file in temp_path.iterdir():
        if not file.is_file():
            continue
        
        for prefix, (folder, name) in DATA_TYPES.items():
            if file.name.startswith(prefix):
                dest_dir = data_path / folder
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), str(dest_dir / f'{name}_{today}.csv'))
                print(f'{folder} 数据已保存')
                break


def main() -> int:
    print(f'当前时间: {datetime.now():%Y-%m-%d %H:%M}\n')
    
    # 获取最新文件夹
    latest = get_latest_folder()
    if not latest:
        print('未找到数据文件夹')
        return 1
    
    print(f'自动获取最新文件夹: {latest}\n')
    
    # 拉取和整理
    data_path, temp_path = get_paths()
    
    if not pull_data(latest, data_path, temp_path):
        return 1
    
    organize_files(temp_path, data_path)
    
    print(f'\n完成！数据保存在: {data_path}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
