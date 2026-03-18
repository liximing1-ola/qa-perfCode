#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APP 启动时间测试工具
支持冷启动和热启动测试
"""
import time
import subprocess
import argparse
from statistics import mean


class StartupTester:
    """启动时间测试类"""
    
    def __init__(self, device: str, package: str, activity: str, wait_time: int = 5):
        self.device = device
        self.package = package
        self.activity = activity
        self.wait_time = wait_time

    def _run_adb(self, cmd: list, check: bool = True) -> subprocess.CompletedProcess:
        """执行 ADB 命令"""
        return subprocess.run(['adb', '-s', self.device] + cmd, 
                            capture_output=True, text=True, check=check)

    def _parse_total_time(self, output: str) -> int | None:
        """从输出中解析 TotalTime"""
        for line in output.splitlines():
            if "TotalTime:" in line:
                try:
                    return int(line.split(":")[1].strip())
                except (ValueError, IndexError):
                    continue
        return None

    def _measure_startup(self, iteration: int, is_cold: bool = True) -> int | None:
        """测量单次启动时间"""
        if is_cold:
            self._run_adb(['shell', 'am', 'force-stop', self.package])
        else:
            # Home 键
            self._run_adb(['shell', 'input', 'keyevent', '3'], check=False)
        
        time.sleep(self.wait_time)
        
        result = self._run_adb(['shell', 'am', 'start', '-W', self.activity], check=False)
        total_time = self._parse_total_time(result.stdout)
        
        if total_time and total_time > 0:
            mode = "冷" if is_cold else "热"
            print(f"第{iteration}次{mode}启动: {total_time}ms")
            return total_time
        
        print(f"第{iteration}次启动未获取到有效数据")
        return None

    def test_cold(self, iterations: int = 30) -> list[int]:
        """冷启动测试"""
        results = []
        for i in range(1, iterations + 1):
            if time_val := self._measure_startup(i, is_cold=True):
                results.append(time_val)
            time.sleep(self.wait_time)
        return results

    def test_hot(self, iterations: int = 30) -> list[int]:
        """热启动测试"""
        # 先执行一次冷启动确保应用已加载
        self._measure_startup(0, is_cold=True)
        
        results = []
        for i in range(1, iterations + 1):
            if time_val := self._measure_startup(i, is_cold=False):
                results.append(time_val)
            time.sleep(self.wait_time)
        return results

    @staticmethod
    def get_device() -> str | None:
        """获取第一个在线设备"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines()[1:]:
                line = line.strip()
                if line.endswith('device'):
                    return line.split('\t')[0]
            print("未找到在线设备")
        except subprocess.CalledProcessError as e:
            print(f"获取设备列表失败: {e.stderr}")
        return None

    @staticmethod
    def calculate_stats(times: list[int]) -> dict:
        """计算统计数据"""
        if len(times) <= 2:
            return {'avg': mean(times), 'max': max(times), 'min': min(times), 'filtered': False}
        
        # 去极值
        filtered = [t for t in times if t not in (max(times), min(times))]
        return {
            'avg': mean(filtered),
            'max': max(times),
            'min': min(times),
            'filtered': True
        }

    @staticmethod
    def save_results(mode: str, times: list[int], output_file: str) -> None:
        """保存测试结果"""
        if not times:
            print("无测试数据可保存")
            return
        
        stats = StartupTester.calculate_stats(times)
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"{mode}启动测试结果\n")
                f.write(f"测试次数: {len(times)}\n")
                f.write(f"原始数据: {times}\n")
                f.write(f"最大值: {stats['max']}ms\n")
                f.write(f"最小值: {stats['min']}ms\n")
                avg_label = "去极值后平均值" if stats['filtered'] else "平均值"
                f.write(f"{avg_label}: {stats['avg']:.2f}ms\n")
            print(f"结果已保存至: {output_file}")
        except IOError as e:
            print(f"保存结果失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='APP 启动时间测试工具')
    parser.add_argument('--mode', required=True, choices=['cold', 'hot'], 
                       help='测试模式: cold(冷启动)/hot(热启动)')
    parser.add_argument('--package', required=True, help='APP 包名')
    parser.add_argument('--activity', required=True, help='APP 主 Activity')
    parser.add_argument('--iterations', type=int, default=30, help='测试次数，默认 30 次')
    parser.add_argument('--output', help='结果输出文件路径')
    args = parser.parse_args()

    device = StartupTester.get_device()
    if not device:
        print("错误: 未找到可用设备")
        return 1

    print(f"设备: {device}, 包名: {args.package}, Activity: {args.activity}")
    
    tester = StartupTester(device, args.package, args.activity)
    times = tester.test_cold(args.iterations) if args.mode == 'cold' else tester.test_hot(args.iterations)
    
    if not times:
        print("未获取到有效测试数据")
        return 1

    stats = StartupTester.calculate_stats(times)
    print(f"\n{args.mode}启动时间统计:")
    print(f"  数据: {times}")
    print(f"  最大: {stats['max']}ms, 最小: {stats['min']}ms")
    avg_label = "去极值平均" if stats['filtered'] else "平均"
    print(f"  {avg_label}: {stats['avg']:.2f}ms")

    if args.output:
        StartupTester.save_results(args.mode, times, args.output)
    
    return 0


if __name__ == '__main__':
    exit(main())

