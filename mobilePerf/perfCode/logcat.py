# -*- coding: utf-8 -*-
import os
import sys
import csv
import time

BaseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))
from mobilePerf.perfCode.androidDevice import AndroidDevice
from mobilePerf.perfCode.common.basemonitor import Monitor
from mobilePerf.perfCode.common.utils import TimeUtils
from mobilePerf.perfCode.common.utils import ms2s
from mobilePerf.perfCode.common.log import logger
from mobilePerf.perfCode.globaldata import RuntimeData


class LogcatMonitor(Monitor):
    def __init__(self, device_id, package=None, **regx_config):
        """构造器
        :param str device_id: 设备id
        :param list package : 监控的进程列表，列表为空时，监控所有进程
        :param dict regx_config : 日志匹配配置项{conf_id = regx}，如：AutoMonitor=ur'AutoMonitor.*:(.*), cost=(\d+)'
        """
        super(LogcatMonitor, self).__init__(**regx_config)
        self.package = package
        self.device_id = device_id
        self.device = AndroidDevice(device_id)  # 设备信息
        self.running = False  # logcat监控器的启动状态(默认：结束状态)
        self.launchtime = LaunchTime(self.device_id, self.package)
        self.exception_log_list = []

    def start(self):
        """启动logcat日志监控器"""
        if self.running:
            logger.warning("logcat monitor is already running")
            return

        # 注册启动日志处理回调函数为handle_launchtime
        self.add_log_handle(self.launchtime.handle_launchTime)
        logger.debug("logcatmonitor start...")
        # 捕获所有进程日志
        # https://developer.android.com/studio/command-line/logcat #alternativeBuffers
        # 默认缓冲区 main system crash,输出全部缓冲区
        self.device.adb.start_logcat(RuntimeData.package_save_path, [], ' -b all')
        time.sleep(1)
        self.running = True

    def stop(self):
        """结束logcat日志监控器"""
        if not self.running:
            logger.warning("logcat monitor is not running")
            return

        logger.debug("logcat monitor: stop...")
        # 删除回调，使用try-except避免handle不存在时抛出异常
        try:
            self.remove_log_handle(self.launchtime.handle_launchTime)
        except ValueError:
            pass

        if self.exception_log_list:
            try:
                self.remove_log_handle(self.handle_exception)
            except ValueError:
                pass

        self.device.adb.stop_logcat()
        self.running = False
        logger.debug("logcat monitor: stopped")

    def parse(self, file_path):
        pass

    def set_exception_list(self, exception_log_list):
        self.exception_log_list = exception_log_list

    def add_log_handle(self, handle):
        """添加实时日志处理器，每产生一条日志，就调用一次handle"""
        self.device.adb._logcat_handle.append(handle)

    def remove_log_handle(self, handle):
        """删除实时日志处理器"""
        self.device.adb._logcat_handle.remove(handle)

    def handle_exception(self, log_line):
        """
        这个方法在每次有log时回调
        :param log_line: 最近一条的log内容
        异常日志写一个日志文件
        :return: void
        """
        # 检查是否匹配任何异常标签
        if not any(tag in log_line for tag in self.exception_log_list):
            return

        logger.debug(f"exception Info: {log_line}")

        # 写入异常日志文件
        try:
            tmp_file = os.path.join(RuntimeData.package_save_path, 'exception.log')
            with open(tmp_file, 'a', encoding="utf-8") as f:
                f.write(f"{log_line}\n")
        except IOError as e:
            logger.error(f"Failed to write exception log: {e}")

        # 获取进程堆栈信息
        if RuntimeData.old_pid:
            process_stack_log_file = os.path.join(
                RuntimeData.package_save_path,
                f'process_stack_{self.package}_{TimeUtils.getCurrentTimeUnderline()}.log'
            )
            try:
                self.device.adb.get_process_stack_from_pid(RuntimeData.old_pid, process_stack_log_file)
            except Exception as e:
                logger.error(f"Failed to get process stack: {e}")


class LaunchTime(object):
    # CSV表头
    CSV_HEADER = ("datetime", "packageName/activity", "this_time(s)", "total_time(s)", "launchType")

    def __init__(self, device_id, package_name=None):
        self.packagename = package_name
        self.device_id = device_id

    @staticmethod
    def _get_launch_tag(log_line):
        """根据日志内容获取启动类型标签"""
        if "am_activity_fully_drawn_time" in log_line:
            return "fullyDrawn launch"
        if "am_activity_launch_time" in log_line:
            return "normal launch"
        return None

    def handle_launchTime(self, log_line):
        """
        这个方法在每次一个启动时间的log产生时回调
        :param log_line: 最近一条的log内容
        :return: void
        """
        ltag = self._get_launch_tag(log_line)
        if not ltag:
            return

        logger.debug(f"launchTime log: {log_line}")

        # 解析日志内容
        try:
            temp_list = log_line.split()[-1].replace("[", "").replace("]", "").split(',')[2:5]
            if len(temp_list) != 3:
                logger.warning(f"Unexpected log format: {log_line}")
                return

            timestamp = time.time()
            content = [
                TimeUtils.formatTimeStamp(timestamp),
                temp_list[0],  # packageName/activity
                temp_list[1],  # this_time
                temp_list[2],  # total_time
                ltag
            ]

            content = self._trim_value(content)
            if content:
                self._update_launch_list(content, timestamp)
        except (IndexError, ValueError) as e:
            logger.error(f"Failed to parse launch time log: {e}")

    @staticmethod
    def _trim_value(content):
        """将毫秒值转换为秒值"""
        try:
            content[2] = ms2s(float(content[2]))  # 将 this_time 转化为s
            content[3] = ms2s(float(content[3]))  # 将 total_time 转化为s
        except (ValueError, IndexError) as e:
            logger.error(f"Failed to trim value: {e}")
            return None
        return content

    def _update_launch_list(self, content, timestamp):
        """更新启动时间列表并写入CSV文件"""
        tmp_file = os.path.join(RuntimeData.package_save_path, 'launch_logcat.csv')

        # 构建perf_data字典（保留原有逻辑）
        perf_data = {
            "task_id": " ",
            'launch_time': [{
                "time": timestamp,
                "act_name": content[1],
                "this_time": content[2],
                "total_time": content[3],
                "launch_type": content[4]
            }],
            'cpu': [],
            "mem": [],
            'traffic': [],
            "fluency": [],
            'power': []
        }

        try:
            # 检查文件是否存在，不存在则写入表头
            file_exists = os.path.exists(tmp_file)
            with open(tmp_file, "a", encoding="utf-8", newline='') as f:
                csvwriter = csv.writer(f, lineterminator='\n')
                if not file_exists:
                    csvwriter.writerow(self.CSV_HEADER)
                csvwriter.writerow(content)
                logger.debug(f"save data to csv: {content}")
        except IOError as e:
            logger.error(f"Failed to write launch time data: {e}")


if __name__ == '__main__':
    pass
