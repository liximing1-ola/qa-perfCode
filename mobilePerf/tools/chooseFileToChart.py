#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoloPi 性能数据拉取和整理工具（手动选择文件夹）

支持交互式选择 SoloPi 测试数据文件夹，自动拉取并整理到对应目录
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
    'PSS_main': ('MEM', 'MEM'),
    'process_main': ('CPU', 'CPU'),
    'CPU 温度_Temperature': ('TEMP', 'TEMP')
}


class ADBError(Exception):
    """ADB 执行异常"""
    pass


def run_adb(cmd: str, timeout: int = 30) -> tuple[int, str, str]:
    """执行 ADB 命令
    
    :param cmd: ADB 命令字符串
    :param timeout: 超时时间（秒）
    :return: (返回码，标准输出，标准错误)
    """
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True,
        encoding='utf-8', timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def check_device() -> bool:
    """检查设备连接
    
    :return: 设备是否在线
    :raises ADBError: ADB 执行失败时
    """
    rc, stdout, stderr = run_adb('adb devices')
    if rc != 0:
        raise ADBError(f'ADB 命令执行失败：{stderr}')
    
    if 'device' not in stdout:
        print('请检查设备 USB 连接')
        return False
    return True


def list_solopi_dirs() -> list[str]:
    """列出 SoloPi 数据目录
    
    :return: 目录名称列表
    :raises ADBError: 无法访问目录时
    """
    cmd = f'adb shell ls /storage/emulated/0/solopi/records/{SOLOPI_PATH}'
    rc, stdout, stderr = run_adb(cmd)
    
    if rc != 0:
        raise ADBError(f'无法访问 SoloPi 目录：{stderr}')
    
    # 过滤有效的目录名（29 字符时间戳）
    return [d for d in stdout.split('\n') if len(d.strip()) == 29]


def pull_data(remote_dir: str, local_path: Path, temp_path: Path) -> None:
    """拉取数据
    
    :param remote_dir: 远程目录名
    :param local_path: 本地保存目录
    :param temp_path: 临时目录
    :raises ADBError: 拉取失败时
    """
    # 清理旧数据
    if temp_path.exists():
        shutil.rmtree(temp_path)
    
    # 拉取数据
    remote = f'/storage/emulated/0/solopi/records/{SOLOPI_PATH}/{remote_dir}'
    print(f'正在拉取：{remote}')
    rc, _, stderr = run_adb(f'adb pull {remote} {local_path}')
    
    if rc != 0:
        raise ADBError(f'拉取数据失败：{stderr}')
    
    # 重命名
    (local_path / remote_dir).rename(temp_path)


def organize_files(temp_path: Path, data_path: Path) -> int:
    """整理文件到对应目录
    
    :param temp_path: 临时目录
    :param data_path: 数据保存目录
    :return: 处理的文件数量
    """
    today = datetime.now().strftime('%Y-%m-%d')
    count = 0
    
    for file in temp_path.iterdir():
        if not file.is_file():
            continue
        
        for prefix, (folder, name) in DATA_TYPES.items():
            if file.name.startswith(prefix):
                dest_dir = data_path / folder
                dest_dir.mkdir(parents=True, exist_ok=True)
                dest_file = dest_dir / f'{name}_{today}.csv'
                shutil.move(str(file), str(dest_file))
                print(f'✓ {folder} 数据已保存：{dest_file.name}')
                count += 1
                break
    
    return count


def select_directory(dirs: list[str]) -> str | None:
    """交互式选择目录
    
    :param dirs: 目录列表
    :return: 选择的目录名，用户取消返回 None
    """
    print('\n可用数据文件夹:')
    for i, d in enumerate(dirs, 1):
        print(f'  {i}. {d}')
    
    choice = input('\n选择文件夹序号 (1=退出): ').strip()
    if choice == '1':
        return None
    
    try:
        idx = int(choice) - 1
        if not (0 <= idx < len(dirs)):
            raise ValueError
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
        data_path = Path(__file__).parent.parent / 'report'
        temp_path = data_path / 'prefData'
        
        pull_data(selected, data_path, temp_path)
        count = organize_files(temp_path, data_path)
        
        print(f'\n完成！共处理 {count} 个文件')
        print(f'数据保存在：{data_path}')
        return 0
        
    except ADBError as e:
        print(f'ADB 错误：{e}')
        return 1
    except Exception as e:
        print(f'未知错误：{e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
