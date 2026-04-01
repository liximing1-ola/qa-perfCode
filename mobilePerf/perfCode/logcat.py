#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logcat 监控模块
监控应用启动时间和异常日志
"""
import csv
import os
import sys
import time
from pathlib import Path

BaseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))

from mobilePerf.perfCode.androidDevice import AndroidDevice
from mobilePerf.perfCode.common.basemonitor import Monitor
from mobilePerf.perfCode.common.utils import TimeUtils, ms2s
from mobilePerf.perfCode.common.log import logger
from mobilePerf.perfCode.globaldata import RuntimeData


class LogcatMonitor(Monitor):
    """Logcat 日志监控器"""

    def __init__(self, device_id: str, package: str | None = None, **config):
        super().__init__(**config)
        self.package = package
        self.device_id = device_id
        self.device = AndroidDevice(device_id)
        self.running = False
        self.launch_time = LaunchTimeHandler(device_id, package)
        self.exception_tags: list[str] = []

    def start(self) -> None:
        """启动监控"""
        if self.running:
            logger.warning("Logcat monitor already running")
            return

        self._add_handler(self.launch_time.handle)
        logger.debug("Logcat monitor starting...")
        
        # 启动 logcat，捕获所有缓冲区
        self.device.adb.start_logcat(RuntimeData.package_save_path, [], '-b all')
        time.sleep(1)
        self.running = True

    def stop(self) -> None:
        """停止监控"""
        if not self.running:
            return

        logger.debug("Logcat monitor stopping...")
        self._remove_handler(self.launch_time.handle)
        
        if self.exception_tags:
            self._remove_handler(self._handle_exception)
        
        self.device.adb.stop_logcat()
        self.running = False
        logger.debug("Logcat monitor stopped")

    def set_exception_tags(self, tags: list[str]) -> None:
        """设置异常日志标签列表"""
        self.exception_tags = tags

    def _add_handler(self, handler) -> None:
        """添加日志处理器"""
        self.device.adb._logcat_handle.append(handler)

    def _remove_handler(self, handler) -> None:
        """移除日志处理器"""
        try:
            self.device.adb._logcat_handle.remove(handler)
        except ValueError:
            pass

    def _handle_exception(self, log_line: str) -> None:
        """处理异常日志"""
        if not any(tag in log_line for tag in self.exception_tags):
            return

        logger.debug(f"Exception: {log_line}")
        
        # 写入异常日志
        log_file = Path(RuntimeData.package_save_path) / 'exception.log'
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{log_line}\n")
        except IOError as e:
            logger.error(f"Failed to write exception log: {e}")

        # 获取进程堆栈
        if RuntimeData.old_pid:
            stack_file = Path(RuntimeData.package_save_path) / f'process_stack_{self.package}_{TimeUtils.getCurrentTimeUnderline()}.log'
            try:
                self.device.adb.dump_stack(RuntimeData.old_pid, str(stack_file))
            except Exception as e:
                logger.error(f"Failed to dump stack: {e}")


class LaunchTimeHandler:
    """启动时间处理器"""
    
    CSV_HEADER = ['datetime', 'package/activity', 'this_time(s)', 'total_time(s)', 'launch_type']
    
    # 启动类型映射
    LAUNCH_PATTERNS = {
        'am_activity_fully_drawn_time': 'fullyDrawn launch',
        'am_activity_launch_time': 'normal launch'
    }

    def __init__(self, device_id: str, package: str | None = None):
        self.package = package
        self.device_id = device_id

    def handle(self, log_line: str) -> None:
        """处理启动时间日志"""
        launch_type = self._detect_launch_type(log_line)
        if not launch_type:
            return

        logger.debug(f"Launch time log: {log_line}")
        
        try:
            data = self._parse_log(log_line, launch_type)
            if data:
                self._save_to_csv(data)
        except (IndexError, ValueError) as e:
            logger.error(f"Failed to parse launch log: {e}")

    def _detect_launch_type(self, log_line: str) -> str | None:
        """检测启动类型"""
        for pattern, launch_type in self.LAUNCH_PATTERNS.items():
            if pattern in log_line:
                return launch_type
        return None

    def _parse_log(self, log_line: str, launch_type: str) -> dict | None:
        """解析日志内容"""
        # 提取 [package/activity,this_time,total_time] 格式
        parts = log_line.split()[-1].strip('[]').split(',')[2:5]
        if len(parts) != 3:
            logger.warning(f"Unexpected log format: {log_line}")
            return None

        try:
            this_time = ms2s(float(parts[1]))
            total_time = ms2s(float(parts[2]))
        except ValueError:
            return None

        return {
            'timestamp': time.time(),
            'datetime': TimeUtils.formatTimeStamp(time.time()),
            'activity': parts[0],
            'this_time': this_time,
            'total_time': total_time,
            'launch_type': launch_type
        }

    def _save_to_csv(self, data: dict) -> None:
        """保存到 CSV"""
        csv_file = Path(RuntimeData.package_save_path) / 'launch_logcat.csv'
        
        row = [
            data['datetime'],
            data['activity'],
            data['this_time'],
            data['total_time'],
            data['launch_type']
        ]

        try:
            file_exists = csv_file.exists()
            with open(csv_file, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, lineterminator='\n')
                if not file_exists:
                    writer.writerow(self.CSV_HEADER)
                writer.writerow(row)
            logger.debug(f"Saved launch data: {row}")
        except IOError as e:
            logger.error(f"Failed to save launch data: {e}")
