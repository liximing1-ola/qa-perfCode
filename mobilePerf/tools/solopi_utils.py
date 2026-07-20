#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SoloPi 数据拉取公共工具模块"""
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from solopi_config import ADB_REMOTE_BASE, DATA_TYPES, SOLOPI_PATH


class ADBError(Exception):
    """ADB 执行异常"""


def run_adb(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """执行 ADB 命令，返回 (returncode, stdout, stderr)"""
    result = subprocess.run(
        cmd, capture_output=True, text=True, encoding='utf-8', timeout=timeout
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_paths() -> tuple[Path, Path]:
    """获取项目路径

    :return: (data_path, temp_path)
    """
    base = Path(__file__).parent.parent
    data_path = base / 'report'
    return data_path, data_path / 'prefData'


def list_solopi_dirs() -> list[str]:
    """列出 SoloPi 数据目录

    :return: 有效的目录名列表（29 字符时间戳）
    :raises ADBError: 设备连接异常
    """
    remote_path = f'{ADB_REMOTE_BASE}/{SOLOPI_PATH}'
    rc, stdout, stderr = run_adb(['adb', 'shell', 'ls', remote_path])

    if rc != 0:
        raise ADBError(f'无法访问 SoloPi 目录：{stderr}')

    return [d.strip() for d in stdout.split('\n') if len(d.strip()) == 29]


def get_latest_folder() -> str | None:
    """获取 SoloPi 最新的数据文件夹

    :return: 最新目录名或 None
    :raises ADBError: 设备连接异常
    """
    dirs = list_solopi_dirs()
    return dirs[-1] if dirs else None


def pull_data(remote_dir: str, data_path: Path, temp_path: Path) -> bool:
    """拉取数据到本地

    :param remote_dir: 远程目录名
    :param data_path: 本地数据根目录
    :param temp_path: 临时目录路径
    :return: 是否成功
    :raises ADBError: 拉取失败
    """
    # 清理旧数据
    if temp_path.exists():
        shutil.rmtree(temp_path)

    # 拉取
    remote = f'{ADB_REMOTE_BASE}/{SOLOPI_PATH}/{remote_dir}'
    print(f'正在拉取：{remote}')
    rc, _, stderr = run_adb(['adb', 'pull', remote, str(data_path)])

    if rc != 0:
        print(f'拉取失败：{stderr}')
        return False

    # 重命名为临时目录
    (data_path / remote_dir).rename(temp_path)
    return True


def organize_files(temp_path: Path, data_path: Path) -> int:
    """整理文件到对应目录

    :param temp_path: 临时目录
    :param data_path: 数据根目录
    :return: 处理的文件数
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
