#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CSV 性能数据可视化工具"""
import argparse
import csv
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

# 跨平台中文字体降级列表
FONT_FALLBACK = ['SimHei', 'PingFang SC', 'Noto Sans CJK SC', 'Arial']


class ChartError(Exception):
    """图表生成异常"""


def get_report_dir() -> Path:
    """获取报告目录"""
    return Path(__file__).parent.parent / 'report'


def find_latest_csv(perf_dir: Path) -> Path | None:
    """查找最新的 CSV 文件"""
    csv_files = list(perf_dir.glob('*.csv'))
    return max(csv_files, key=lambda p: p.stat().st_mtime) if csv_files else None


def parse_csv(csv_path: Path, perf_type: str) -> list[int]:
    """解析 CSV 文件，返回数据列表"""
    if perf_type not in PERF_CONFIG:
        raise ChartError(f"不支持的性能类型：{perf_type}")

    config = PERF_CONFIG[perf_type]
    values: list[int] = []

    # 优先 UTF-8，GBK 降级
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)
            rows = list(reader)
    except UnicodeDecodeError:
        with open(csv_path, 'r', encoding='gbk') as f:
            reader = csv.reader(f)
            next(reader, None)
            rows = list(reader)

    for row in rows:
        try:
            val = round(float(row[1]))
            if config['filter'](val):
                values.append(val)
        except (IndexError, ValueError):
            continue

    # 降采样
    del values[1::2]

    # 去极值：各移除一个最大值和一个最小值
    if config['remove_extremes'] and len(values) > 2:
        max_idx = values.index(max(values))
        del values[max_idx]
        min_idx = values.index(min(values))
        del values[min_idx]

    if values:
        print(f"min: {min(values)}, max: {max(values)}, avg: {sum(values) // len(values)}")

    return values


def create_chart(data: list[int], perf_type: str, output_path: Path) -> None:
    """创建性能图表"""
    config = PERF_CONFIG[perf_type]

    # 设置图表样式
    plt.rcParams.update({
        'figure.figsize': (8, 4),
        'savefig.dpi': 200,
        'figure.dpi': 100,
        'font.sans-serif': FONT_FALLBACK,
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


def main() -> int:
    """主函数"""
    parser = argparse.ArgumentParser(description='CSV 性能数据可视化工具')
    parser.add_argument(
        'perf_type',
        choices=[t.lower() for t in PERF_CONFIG],
        help='性能类型 (fps/cpu/mem/temp)'
    )
    parser.add_argument(
        '-f', '--file',
        type=Path,
        help='指定 CSV 文件路径（默认自动查找最新文件）'
    )
    args = parser.parse_args()

    perf_type = args.perf_type.upper()

    try:
        # 获取 CSV 路径
        if args.file:
            csv_path = args.file
            if not csv_path.exists():
                print(f"文件不存在：{csv_path}")
                return 1
        else:
            csv_file = find_latest_csv(get_report_dir() / perf_type)
            if not csv_file:
                print(f"未找到 {perf_type} 的 CSV 文件")
                return 1
            csv_path = csv_file

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
    except Exception as e:
        print(f"未知错误：{e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
