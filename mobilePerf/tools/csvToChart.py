#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 性能数据可视化工具

支持 FPS、CPU、MEM、TEMP 数据的图表生成
自动查找最新 CSV 文件或指定文件路径
"""
import csv
import platform
import sys
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt

# 性能指标配置
PERF_CONFIG = {
    'FPS': {
        'y_name': 'FPS(gfxinfo)',
        'filter': lambda v: 0 < v <= 90,
        'remove_extremes': False,
        'color': '#2ecc71'
    },
    'CPU': {
        'y_name': 'CPU(%)',
        'filter': lambda v: 0 < v <= 100,
        'remove_extremes': True,
        'color': '#e74c3c'
    },
    'MEM': {
        'y_name': 'MEM(m)',
        'filter': lambda v: v > 0,
        'remove_extremes': True,
        'color': '#3498db'
    },
    'TEMP': {
        'y_name': 'Temp(℃)',
        'filter': lambda v: v > 0,
        'remove_extremes': True,
        'color': '#f39c12'
    }
}


class ChartError(Exception):
    """图表生成异常"""
    pass


def get_report_dir() -> Path:
    """获取报告目录"""
    return Path(__file__).parent.parent / 'report'


def find_latest_csv(perf_dir: Path) -> Path | None:
    """查找最新的 CSV 文件
    
    :param perf_dir: 性能数据目录
    :return: 最新的 CSV 文件路径，不存在返回 None
    """
    csv_files = list(perf_dir.glob('*.csv'))
    return max(csv_files, key=lambda p: p.stat().st_mtime) if csv_files else None


def parse_csv(csv_path: Path, perf_type: str) -> list[int]:
    """解析 CSV 文件，返回数据列表
    
    :param csv_path: CSV 文件路径
    :param perf_type: 性能类型
    :return: 数据列表
    :raises ChartError: 解析失败时
    """
    if perf_type not in PERF_CONFIG:
        raise ChartError(f"不支持的性能类型：{perf_type}")
    
    config = PERF_CONFIG[perf_type]
    values = []
    
    try:
        with open(csv_path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader, None)  # 跳过表头
            for row in reader:
                try:
                    val = round(float(row[1]))
                    if config['filter'](val):
                        values.append(val)
                except (IndexError, ValueError):
                    continue
    except UnicodeDecodeError:
        # 尝试 UTF-8 编码
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            for row in reader:
                try:
                    val = round(float(row[1]))
                    if config['filter'](val):
                        values.append(val)
                except (IndexError, ValueError):
                    continue
    
    # 降采样（删除每隔一个元素）
    del values[1::2]
    
    # 去极值
    if config['remove_extremes'] and len(values) > 2:
        values.remove(max(values))
        values.remove(min(values))
    
    if values:
        print(f"min: {min(values)}, max: {max(values)}, avg: {sum(values)//len(values)}")
    
    return values


def create_chart(data: list[int], perf_type: str, output_path: Path) -> None:
    """创建性能图表
    
    :param data: 数据列表
    :param perf_type: 性能类型
    :param output_path: 输出路径
    """
    config = PERF_CONFIG[perf_type]
    
    # 设置图表样式
    plt.rcParams.update({
        'figure.figsize': (8, 4),
        'savefig.dpi': 200,
        'figure.dpi': 100,
        'font.sans-serif': ['SimHei', 'Arial'],  # 支持中文
        'axes.unicode_minus': False
    })
    
    x = range(1, len(data) + 1)
    plt.plot(x, data, color=config['color'], linewidth=1.5)
    plt.xlabel('Time Consuming', color='r')
    plt.ylabel(config['y_name'], color='r', size=16)
    plt.title(f'APP_{perf_type}_Analysis', color='g', size=18)
    plt.grid(True, alpha=0.3)
    plt.savefig(output_path)
    plt.show()


def get_csv_path(platform_type: str, args: list[str]) -> tuple[Path, str]:
    """根据平台类型获取 CSV 路径和性能类型
    
    :param platform_type: 平台类型 (win/mac)
    :param args: 命令行参数
    :return: (CSV 路径，性能类型)
    :raises FileNotFoundError: 文件不存在
    :raises ValueError: 参数错误
    """
    report_dir = get_report_dir()
    
    if platform_type == 'win':
        print('Platform: Windows')
        if len(args) >= 2:
            # 指定文件路径
            return Path(args[0]), args[1].upper()
        elif len(args) == 1:
            # 自动查找最新文件
            perf = args[0].upper()
            csv_file = find_latest_csv(report_dir / perf)
            if not csv_file:
                raise FileNotFoundError(f"未找到 {perf} 的 CSV 文件")
            return csv_file, perf
        else:
            raise ValueError("Windows 模式需要至少 1 个参数")
    
    elif platform_type == 'mac':
        print('Platform: macOS')
        if len(args) != 1:
            raise ValueError("macOS 模式需要输入一个参数，如：cpu, mem, fps")
        perf = args[0].upper()
        csv_file = find_latest_csv(report_dir / perf)
        if not csv_file:
            raise FileNotFoundError(f"未找到 {perf} 的 CSV 文件")
        return csv_file, perf
    
    else:
        raise ValueError(f"不支持的平台：{platform_type}")


def main() -> int:
    """主函数"""
    try:
        # 检测平台
        sys_platform = platform.system()
        if sys_platform == 'Windows':
            platform_type = 'win'
        elif sys_platform == 'Darwin':
            platform_type = 'mac'
        else:
            print(f"不支持的平台：{sys_platform}")
            return 1
        
        csv_path, perf_type = get_csv_path(platform_type, sys.argv[1:])
        print(f"CSV: {csv_path}, Type: {perf_type}")
        
        data = parse_csv(csv_path, perf_type)
        if not data:
            print("无有效数据")
            return 1
        
        output_path = get_report_dir() / perf_type / f"{datetime.now():%Y-%m-%d}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        create_chart(data, perf_type, output_path)
        print(f"图表已保存：{output_path}")
        return 0
        
    except ChartError as e:
        print(f"图表错误：{e}")
        return 1
    except FileNotFoundError as e:
        print(f"文件错误：{e}")
        return 1
    except ValueError as e:
        print(f"参数错误：{e}")
        return 1
    except Exception as e:
        print(f"未知错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
