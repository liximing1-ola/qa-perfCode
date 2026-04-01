#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CPU 监控模块
通过 top 命令采集 CPU 性能数据
"""
import csv
import os
import re
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

BaseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))
from mobilePerf.perfCode.common.config import config
from mobilePerf.perfCode.androidDevice import AndroidDevice
from mobilePerf.perfCode.common.utils import TimeUtils
from mobilePerf.perfCode.common.log import logger
from mobilePerf.perfCode.globaldata import RuntimeData


@dataclass
class CpuStats:
    """CPU 统计信息"""
    user_rate: str = ''
    system_rate: str = ''
    nice_rate: str = ''
    idle_rate: str = ''
    iow_rate: str = ''
    irq_rate: str = ''
    device_rate: int = 0


@dataclass
class PackageInfo:
    """包信息"""
    package: str
    pid: str = ''
    pid_cpu: str = ''
    uid: str = ''


class PckCpuInfo:
    """解析 top 命令输出的 CPU 信息"""
    
    # Android < 8.0: User 0%, System 0%, IOW 0%, IRQ 0%
    RE_CPU_OLD = re.compile(r'User (\d+)%, System (\d+)%, IOW (\d+)%, IRQ (\d+)%')
    # Android >= 8.0: 400%cpu 56%user 1%nice 46%sys 285%idle 0%iow 10%irq 2%sirq 0%host
    RE_CPU_NEW = re.compile(
        r'(\d+)%cpu\s+(\d+)%user\s+(\d+)%nice\s+(\d+)%sys\s+(\d+)%idle\s+(\d+)%iow\s+(\d+)%irq\s+(\d+)%sirq'
    )

    def __init__(self, packages: list[str], source: str, sdk_version: int):
        self.source = source
        self.sdk_version = sdk_version
        self.packages = packages
        self.stats = CpuStats()
        self.package_list: list[PackageInfo] = []
        self.total_pid_cpu = 0.0
        self._parse()

    def _parse(self) -> None:
        """解析 CPU 和包信息"""
        self._parse_cpu_usage()
        self._parse_packages()

    def _parse_cpu_usage(self) -> None:
        """解析 CPU 使用率"""
        if self.sdk_version < 26:
            match = self.RE_CPU_OLD.search(self.source)
            if match:
                self.stats.user_rate = match.group(1)
                self.stats.system_rate = match.group(2)
                self.stats.iow_rate = match.group(3)
                self.stats.irq_rate = match.group(4)
                self.stats.device_rate = int(self.stats.user_rate) + int(self.stats.system_rate)
        else:
            match = self.RE_CPU_NEW.search(self.source)
            if match:
                self.stats.user_rate = match.group(2)
                self.stats.nice_rate = match.group(3)
                self.stats.system_rate = match.group(4)
                self.stats.idle_rate = match.group(5)
                self.stats.iow_rate = match.group(6)
                self.stats.irq_rate = match.group(7)
                self.stats.device_rate = int(self.stats.user_rate) + int(self.stats.system_rate)
        
        logger.debug(f"CPU stats: device={self.stats.device_rate}%, user={self.stats.user_rate}%")

    def _parse_packages(self) -> None:
        """解析包 CPU 信息"""
        if not self.packages:
            logger.error("No packages specified")
            return

        cpu_idx = self._get_column_index(["CPU]", "CPU%"], 2)
        uid_idx = self._get_column_index(["UID", "USER"], 8)

        for package in self.packages:
            info = PackageInfo(package=package)
            
            for line in self.source.split('\n'):
                if package not in line:
                    continue
                
                parts = line.split()
                if len(parts) < 2:
                    continue
                
                target_pkg = parts[-1]
                if package != target_pkg:
                    continue
                
                pid = parts[0]
                if not pid.isdigit() or int(pid) <= 0:
                    continue
                
                info.pid = pid
                if len(parts) > cpu_idx:
                    info.pid_cpu = parts[cpu_idx].replace('%', '')
                    self.total_pid_cpu += float(info.pid_cpu)
                if len(parts) > uid_idx:
                    info.uid = parts[uid_idx]
                
                logger.debug(f"Package {package}: pid={pid}, cpu={info.pid_cpu}%")
                break
            
            self.package_list.append(info)

    def _get_column_index(self, names: list[str], default: int) -> int:
        """获取列索引"""
        for line in self.source.split('\n'):
            parts = re.split(r'[%\s]+', line.strip())
            for name in names:
                if name in parts:
                    return parts.index(name)
        return default

    @property
    def device_cpu_rate(self) -> int:
        return self.stats.device_rate

    @property
    def user_rate(self) -> str:
        return self.stats.user_rate

    @property
    def system_rate(self) -> str:
        return self.stats.system_rate

    @property
    def idle_rate(self) -> str:
        return self.stats.idle_rate

    def sum_procs_cpurate(self) -> None:
        """计算所有进程 CPU% 之和"""
        if not self.source or not self.package_list:
            return
        
        uid = self.package_list[0].uid if self.package_list else ""
        if not uid:
            return
        
        total = sum(
            int(line.split()[self._get_column_index(["CPU]", "CPU%"], 2)].replace("%", ""))
            for line in self.source.split("\n")
            if uid in line and len(line.split()) > 2
        )
        
        uid_rate = f"{total}%"
        for pkg in self.package_list:
            pkg.uid_cpu = uid_rate
        logger.debug(f"Sum CPU rate for uid {uid}: {uid_rate}")


class CpuCollector:
    """CPU 数据采集器"""
    
    MAX_FILE_SIZE_MB = 100
    DEFAULT_SDK = 25

    def __init__(self, device, packages: list[str], interval: int = 1, timeout: int = 24 * 60 * 60):
        self.device = device
        self.packages = packages
        self._interval = interval
        self._timeout = timeout
        self._stop_event = threading.Event()
        self.cpu_list: list = []
        self.sdkversion = self._get_sdk_version()
        self._top_pipe = None
        self._thread = None
        
        # 检测 top 命令参数支持
        self.top_cmd = self._detect_top_cmd()
        logger.debug(f"SDK version: {self.sdkversion}, top cmd: {self.top_cmd}")

    def _detect_top_cmd(self) -> str:
        """检测并返回合适的 top 命令"""
        cmd = f'top -b -n 1 -d {self._interval}'
        ret = self.device.adb.run_shell_cmd(cmd)
        if ret and 'Invalid argument "-b"' in ret:
            logger.debug("top -b not supported, using fallback")
            return f'top -n 1 -d {self._interval}'
        return cmd

    def _get_sdk_version(self) -> int:
        """获取 SDK 版本"""
        sdk = self.device.adb.get_sdk_version()
        return sdk if sdk is not None else self.DEFAULT_SDK

    def start(self, start_time: str) -> None:
        """启动采集线程"""
        self._thread = threading.Thread(target=self._collect_loop, args=(start_time,), daemon=True)
        self._thread.start()
        logger.debug("CpuCollector started")

    def stop(self) -> None:
        """停止采集"""
        logger.debug("CpuCollector stopping...")
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        
        if self._top_pipe and self._top_pipe.poll() is None:
            self._top_pipe.terminate()

    def _run_top(self) -> str | None:
        """执行 top 命令并返回输出"""
        self._top_pipe = self.device.adb.run_shell_cmd(self.top_cmd, sync=False)
        if not self._top_pipe:
            return None
        
        out, err = self._top_pipe.communicate()
        if err:
            logger.error(f"top command error: {err}")
            return None
        
        result = out.decode('utf-8').replace('\r', '') if isinstance(out, bytes) else out.replace('\r', '')
        self._save_top_log(result)
        return result

    def _save_top_log(self, content: str) -> None:
        """保存 top 日志"""
        if not RuntimeData.package_save_path:
            return
        
        top_file = Path(RuntimeData.package_save_path) / 'top.txt'
        with open(top_file, "a+", encoding="utf-8") as f:
            f.write(f"{TimeUtils.getCurrentTime()} top info:\n{content}\n\n")
        
        # 清理大文件
        if top_file.stat().st_size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            top_file.unlink()

    def _collect_loop(self, start_time: str) -> None:
        """采集循环"""
        end_time = time.time() + self._timeout
        cpu_file = Path(RuntimeData.package_save_path) / 'cpuInfo.csv'
        
        # 写入表头
        headers = ["datetime", "device_cpu_rate%", "user%", "system%", "idle%"]
        for _ in self.packages:
            headers.extend(["package", "pid", "pid_cpu%"])
        if len(self.packages) > 1:
            headers.append("total_pid_cpu%")
        
        with open(cpu_file, 'w', newline='', encoding="utf-8") as f:
            csv.writer(f).writerow(headers)
        
        while not self._stop_event.is_set() and time.time() < end_time:
            try:
                before = time.time()
                cpu_info = self._run_top()
                elapsed = time.time() - before
                
                if not cpu_info:
                    continue
                
                parsed = PckCpuInfo(self.packages, cpu_info, self.sdkversion)
                if not parsed.package_list:
                    continue
                
                # 构建数据行
                row = [
                    TimeUtils.getCurrentTime(),
                    str(parsed.device_cpu_rate),
                    parsed.user_rate,
                    parsed.system_rate,
                    parsed.idle_rate
                ]
                
                for pkg_info in parsed.package_list:
                    row.extend([pkg_info.package, pkg_info.pid, pkg_info.pid_cpu])
                
                if len(self.packages) > 1:
                    row.append(parsed.total_pid_cpu)
                
                # 写入 CSV
                with open(cpu_file, 'a', newline='', encoding="utf-8") as f:
                    csv.writer(f).writerow(row)
                
                logger.info(f"CPU data saved: {row[:5]}")
                
                # 调整采集间隔
                sleep_time = self._interval - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"CPU collection error: {e}")
                logger.debug(traceback.format_exc())


class CpuMonitor:
    """CPU 监控器"""

    def __init__(self, device_id: str | None, packages: list[str], interval: int = 5, timeout: int = 24 * 60 * 60):
        self.device = AndroidDevice(device_id)
        self.packages = packages
        self.collector = CpuCollector(self.device, packages, interval, timeout)

    def start(self, start_time: str) -> None:
        """启动监控"""
        self._ensure_save_path()
        self.collector.start(start_time)
        logger.debug("CpuMonitor started")

    def _ensure_save_path(self) -> None:
        """确保保存路径存在"""
        if not RuntimeData.package_save_path and self.packages:
            path = Path.cwd().parent.parent / 'results' / self.packages[0]
            path.mkdir(parents=True, exist_ok=True)
            RuntimeData.package_save_path = str(path)

    def stop(self) -> None:
        """停止监控"""
        self.collector.stop()
        logger.debug("CpuMonitor stopped")


# ============== 图表功能（可选） ==============

try:
    from pylab import plt
    HAS_PLT = True
except ImportError:
    HAS_PLT = False


def csv_to_list(csv_path: str, column: int = 7) -> list[float]:
    """读取 CSV 指定列数据"""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过表头
        return [round(float(row[column])) for row in reader if len(row) > column]


def chart_cpu(x: list, y: list, title: str, filename: str) -> None:
    """绘制 CPU 图表"""
    if not HAS_PLT:
        logger.warning("matplotlib not available, skipping chart")
        return
    
    if not y or len(x) != len(y):
        raise ValueError("x and y must have same length")
    
    plt.plot(x, y)
    plt.xlabel('Time(Min)', color='r')
    plt.ylabel('CPU(*%)', color='r')
    plt.title(title, color='g')
    plt.grid(True)
    plt.savefig(f'E:/report/{filename}.png')
    plt.show()


# ============== 测试入口 ==============

def main_cpu(num: int) -> None:
    """测试 CPU 采集"""
    monitor = CpuMonitor(config.deviceId, [config.package], 20)
    monitor.start(TimeUtils.getCurrentTimeUnderline())
    time.sleep(20 * num)
    monitor.stop()


def main_chart() -> None:
    """测试图表生成"""
    csv_path = 'E:/mobileperf/results/com.imbb.banban.android/cpuInfo.csv'
    y = csv_to_list(csv_path)
    if len(y) == 30:
        chart_cpu(list(range(1, 31)), y, 'chatroom-CPU', 'banban')


if __name__ == "__main__":
    main_chart()
