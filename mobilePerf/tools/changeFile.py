#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SoloPi 性能数据自动拉取工具

自动从设备拉取最新的 SoloPi 性能测试数据，并整理到对应目录
支持 FPS、CPU、MEM、TEMP 等数据类型
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
    'CPU 温度_Temperature': ('TEMP', 'TEMP')
}


class ADBError(Exception):
    """ADB 执行异常"""
    pass


def run_adb(cmd: str) -> tuple[int, str, str]:
    """执行 ADB 命令
    
    :param cmd: ADB 命令字符串
    :return: (返回码，标准输出，标准错误)
    """
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, encoding='utf-8'
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_paths() -> tuple[Path, Path]:
    """获取项目路径
    
    :return: (报告目录，prefData 目录)
    """
    base = Path(__file__).parent.parent
    data_path = base / 'report'
    return data_path, data_path / 'prefData'


def get_latest_folder() -> str | None:
    """获取 SoloPi 最新的数据文件夹
    
    :return: 最新的文件夹名称，失败返回 None
    :raises ADBError: ADB 执行失败时
    """
    cmd = f'adb shell ls /storage/emulated/0/solopi/records/{SOLOPI_PATH}'
    rc, stdout, stderr = run_adb(cmd)
    
    if rc != 0:
        raise ADBError(f'请检查设备连接或 SoloPi 目录：{stderr}')
    
    # 获取有效的目录名（29 字符时间戳）并返回最新的
    dirs = [d.strip() for d in stdout.split('\n') if len(d.strip()) == 29]
    return dirs[-1] if dirs else None


def pull_data(remote_dir: str, data_path: Path, temp_path: Path) -> bool:
    """拉取数据到本地
    
    :param remote_dir: 远程目录名
    :param data_path: 数据保存目录
    :param temp_path: 临时目录
    :return: 是否成功
    """
    # 清理旧数据
    if temp_path.exists():
        shutil.rmtree(temp_path)
    
    # 拉取
    remote = f'/storage/emulated/0/solopi/records/{SOLOPI_PATH}/{remote_dir}'
    print(f'正在拉取：{remote}')
    rc, _, stderr = run_adb(f'adb pull {remote} {data_path}')
    
    if rc != 0:
        print(f'拉取失败：{stderr}')
        return False
    
    # 重命名为临时目录
    (data_path / remote_dir).rename(temp_path)
    return True


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
    except Exception as e:
        print(f'未知错误：{e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
