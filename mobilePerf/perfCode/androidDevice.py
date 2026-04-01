#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADB 设备管理模块
提供 Android 设备的 ADB 连接、命令执行、日志收集等功能
"""
import os
import platform
import re
import subprocess
import sys
import threading
import time
import traceback
from pathlib import Path

BaseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))
from mobilePerf.perfCode.common.log import logger
from mobilePerf.perfCode.common.utils import TimeUtils
from mobilePerf.perfCode.globaldata import RuntimeData


class ADB:
    """ADB 工具类"""
    _os_name: str | None = None
    _adb_path: str | None = None
    _device_pattern = re.compile(r'^(\S+)\tdevice$')

    def __init__(self, device_id: str | None = None):
        self._device_id = device_id
        self._adb_path = self.get_adb_path()
        self._logcat_handle: list = []
        self._logcat_running = False
        self._log_pipe = None
        self._system_version: str | None = None
        self._sdk_version: int | None = None
        self._phone_brand: str | None = None
        self._phone_model: str | None = None
        self.before_connect = True
        self.after_connect = True

    @property
    def device_id(self) -> str | None:
        """设备 ID"""
        return self._device_id

    @staticmethod
    def get_adb_path() -> str:
        """获取 ADB 可执行文件路径"""
        if ADB._adb_path:
            return ADB._adb_path

        # 1. 检查环境变量
        env_path = os.environ.get('ADB_PATH')
        if env_path and env_path.endswith('adb.exe'):
            ADB._adb_path = env_path
            return ADB._adb_path

        # 2. 检查系统 adb
        try:
            result = subprocess.run(
                ['adb', 'devices'], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0 and "command not found" not in result.stdout:
                ADB._adb_path = "adb"
                logger.debug("Using system adb")
                return ADB._adb_path
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # 3. 使用内置 adb
        logger.debug("Using bundled adb")
        cur_path = Path(__file__).parent
        ADB._os_name = platform.system()
        
        if ADB._os_name == "Windows":
            ADB._adb_path = str(cur_path / "adb.exe")
        elif ADB._os_name == "Darwin":
            ADB._adb_path = str(cur_path / "platform-tools-latest-darwin" / "platform-tools" / "adb")
        else:
            ADB._adb_path = str(cur_path / "platform-tools-latest-linux" / "platform-tools" / "adb")
        
        return ADB._adb_path

    @staticmethod
    def get_os_name() -> str:
        """获取操作系统名称"""
        if ADB._os_name is None:
            ADB._os_name = platform.system()
        return ADB._os_name

    @staticmethod
    def list_devices() -> list[str]:
        """获取已连接的设备列表"""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                return []
            
            devices = []
            for line in result.stdout.replace('\r', '').splitlines()[1:]:
                match = ADB._device_pattern.match(line)
                if match:
                    devices.append(match.group(1))
            
            logger.debug(f"Found devices: {devices}")
            return devices
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"Failed to list devices: {e}")
            return []

    @staticmethod
    def is_connected(device_id: str) -> bool:
        """检查设备是否已连接"""
        return device_id in ADB.list_devices()

    @staticmethod
    def recover() -> None:
        """恢复 ADB 连接"""
        if ADB.check_adb_normal():
            logger.debug("ADB is normal")
            return
        
        logger.error("ADB is not normal, restarting...")
        ADB.kill_server()
        ADB.start_server()

    @staticmethod
    def check_adb_normal() -> bool:
        """检查 ADB 服务是否正常"""
        try:
            result = subprocess.run(
                ['adb', 'devices'],
                capture_output=True,
                text=True,
                timeout=10
            )
            output = result.stdout
            logger.debug(f"ADB check output: {output}")
                
            if "daemon not running" in output:
                logger.warning("ADB daemon not running")
                return False
            elif "ADB server didn't ACK" in output:
                logger.warning("ADB server error, port 5037 may be occupied")
                return False
            return True
        except (subprocess.TimeoutExpired, Exception) as e:
            logger.error(f"ADB check failed: {e}")
            return False
    
    @staticmethod
    def kill_server() -> None:
        """停止 ADB 服务"""
        logger.warning("Killing ADB server...")
        subprocess.run(['adb', 'kill-server'], capture_output=True)
    
    @staticmethod
    def start_server() -> None:
        """启动 ADB 服务"""
        ADB._kill_5037_process()
        logger.warning("Starting ADB server...")
        subprocess.run(['adb', 'start-server'], capture_output=True)
    
    @staticmethod
    def _kill_5037_process() -> None:
        """杀死占用 5037 端口的进程（仅 Windows）"""
        if ADB.get_os_name() != "Windows":
            return
            
        try:
            # 查找占用 5037 端口的进程
            result = subprocess.run(
                ['netstat', '-ano'],
                capture_output=True,
                text=True
            )
                
            for line in result.stdout.splitlines():
                if ':5037' in line and 'LISTENING' in line:
                    parts = line.split()
                    pid = parts[-1]
                    logger.debug(f"Found process {pid} occupying port 5037")
                        
                    # 获取进程名
                    task_result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True,
                        text=True
                    )
                        
                    if task_result.returncode == 0:
                        logger.warning(f"Killing process {pid} on port 5037")
                        subprocess.run(
                            ['taskkill', '/T', '/F', '/PID', pid],
                            capture_output=True
                        )
                    break
        except Exception as e:
            logger.error(f"Failed to kill 5037 process: {e}")

    def _run_cmd(
        self, 
        cmd: str, 
        *args: str, 
        sync: bool = True, 
        timeout: int = 10, 
        retry: int = 1
    ) -> subprocess.Popen | str | None:
        """执行 ADB 命令
        
        :param cmd: ADB 子命令
        :param args: 额外参数
        :param sync: 是否同步等待结果
        :param timeout: 超时时间（秒）
        :param retry: 重试次数
        :return: 同步模式返回输出字符串，异步模式返回 Popen 对象
        """
        # 构建命令
        base_cmd = [self._adb_path]
        if self._device_id:
            base_cmd.extend(['-s', self._device_id])
        base_cmd.append(cmd)
        base_cmd.extend(args)
        
        cmd_str = ' '.join(base_cmd)
        logger.debug(f"ADB command: {cmd_str}")
        
        for attempt in range(retry):
            try:
                process = subprocess.Popen(
                    cmd_str,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True
                )
                
                if not sync:
                    return process
                
                # 同步执行，带超时
                start_time = time.time()
                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    logger.warning(f"Command timeout after {timeout}s: {cmd_str}")
                    if attempt < retry - 1:
                        continue
                    return None
                
                # 检查错误
                if process.returncode != 0:
                    error_msg = stderr or stdout
                    if self._handle_error(error_msg):
                        return ""
                
                # 使用 stderr 如果 stdout 为空
                result = stdout if stdout else stderr
                elapsed = time.time() - start_time
                logger.info(f"Command completed in {elapsed:.2f}s")
                
                return result.strip() if result else ""
                
            except Exception as e:
                logger.error(f"Command failed: {e}")
                if attempt < retry - 1:
                    time.sleep(0.5)
                    continue
                return None
        
        return None
    
    def _handle_error(self, error_msg: str) -> bool:
        """处理 ADB 错误，返回 True 表示已处理"""
        error_patterns = {
            'no devices/emulators found': 'No device found, please reconnect',
            'device not found': 'Device disconnected, please reconnect',
            'device offline': 'Device offline, please reconnect',
            'killing': 'ADB port 5037 occupied',
            'more than one device': 'Multiple devices, please specify device ID',
        }
        
        for pattern, message in error_patterns.items():
            if pattern in error_msg.lower():
                logger.error(f"{message}: {error_msg}")
                if 'device' in pattern:
                    self.before_connect = False
                    self.after_connect = False
                return True
        
        return False

    def run_adb_cmd(self, cmd: str, *args: str, **kwargs) -> str | None:
        """执行 ADB 命令（带重试）"""
        retry = kwargs.get('retry', 3)
        return self._run_cmd(cmd, *args, retry=retry, **kwargs)

    def run_shell_cmd(self, cmd: str, **kwargs) -> str | None:
        """执行 adb shell 命令"""
        # 记录重连信息
        if not self.before_connect and self.after_connect:
            self._log_reconnect()
        
        result = self._run_cmd('shell', cmd, **kwargs)
        if result is None:
            logger.error(f'Shell command failed: {cmd}')
        return result
    
    def _log_reconnect(self) -> None:
        """记录设备重连信息"""
        try:
            uptime = self._run_cmd('shell', 'cat /proc/uptime', retry=1)
            if uptime and RuntimeData.package_save_path:
                log_file = os.path.join(RuntimeData.package_save_path, "uptime.txt")
                with open(log_file, "a+", encoding="utf-8") as f:
                    f.write(f"{TimeUtils.get_current_time_underline()} /proc/uptime:{uptime}\n")
                self.before_connect = True
        except Exception as e:
            logger.error(f"Failed to log reconnect: {e}")

    def _logcat_worker(self, save_dir: str, params: str = "") -> None:
        """Logcat 采集线程工作函数"""
        logs: list[str] = []
        line_count = 0
        file_line_count = 0
        file_time = TimeUtils.get_current_time_underline()
        empty_count = 0
        
        while self._logcat_running:
            try:
                log = self._log_pipe.stdout.readline()
                if not log:
                    empty_count += 1
                    if empty_count % 1000 == 0:
                        logger.info("Logcat output empty, restarting...")
                        self._log_pipe = self.run_shell_cmd(f'logcat -v threadtime {params}', sync=False)
                    continue
                
                empty_count = 0
                log = log.strip()
                
                # 调用注册的处理器
                for handler in self._logcat_handle:
                    try:
                        handler(log)
                    except Exception as e:
                        logger.error(f"Logcat handler error: {e}")
                
                logs.append(log)
                line_count += 1
                file_line_count += 1
                
                # 每 100 行写入一次文件
                if line_count >= 100:
                    self._save_logs(save_dir, f'logcat_{file_time}.log', logs)
                    logs = []
                    line_count = 0
                
                # 每 60 万行创建新文件
                if file_line_count >= 600000:
                    file_time = TimeUtils.get_current_time_underline()
                    file_line_count = 0
                    
            except Exception as e:
                logger.error(f"Logcat thread error: {e}")
                logger.debug(traceback.format_exc())
    
    def _save_logs(self, save_dir: str, filename: str, logs: list[str]) -> None:
        """保存日志到文件"""
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'a+', encoding="utf-8") as f:
            f.write('\n'.join(logs) + '\n')

    def start_logcat(self, save_dir: str, process_list: list | None = None, params: str = '') -> None:
        """启动 logcat 采集
        
        :param save_dir: 日志保存目录
        :param process_list: 进程过滤列表（暂未使用）
        :param params: 额外参数
        """
        if self._logcat_running:
            logger.warning('Logcat already running')
            return
        
        os.makedirs(save_dir, exist_ok=True)
        
        # 清除缓冲区
        try:
            self.run_shell_cmd(f'logcat -c {params}')
        except Exception as e:
            logger.warning(f"Failed to clear logcat buffer: {e}")
        
        self._logcat_running = True
        self._log_pipe = self.run_shell_cmd(f'logcat -v threadtime {params}', sync=False)
        
        self._logcat_thread = threading.Thread(
            target=self._logcat_worker,
            args=(save_dir, params),
            daemon=True
        )
        self._logcat_thread.start()
        logger.debug("Logcat started")

    def stop_logcat(self) -> None:
        """停止 logcat 采集"""
        self._logcat_running = False
        logger.debug("Stopping logcat...")
        
        if hasattr(self, '_log_pipe') and self._log_pipe:
            try:
                if self._log_pipe.poll() is None:
                    self._log_pipe.terminate()
                    self._log_pipe.wait(timeout=2)
            except Exception as e:
                logger.warning(f"Error stopping logcat: {e}")

    def wait_for_device(self, timeout: int = 180) -> bool:
        """等待设备连接"""
        result = self.run_adb_cmd("wait-for-device", timeout=timeout)
        if not result:
            logger.warning("wait-for-device timeout")
            return False
        return True

    def bugreport(self, save_path: str) -> str | None:
        """收集 bugreport"""
        return self.run_adb_cmd('bugreport', save_path, timeout=180)

    # ==================== 文件操作 ====================

    def push_file(self, src_path: str, dst_path: str, retries: int = 3) -> str | None:
        """推送文件到设备
        
        :param src_path: 本地文件路径
        :param dst_path: 设备目标路径
        :param retries: 重试次数
        :return: 命令执行结果
        """
        src = Path(src_path)
        if not src.exists():
            logger.error(f"Source file not found: {src_path}")
            return None
        
        file_size = src.stat().st_size
        # 处理路径空格
        src_quoted = f'"{src_path}"' if " " in src_path else src_path
        
        for attempt in range(retries):
            result = self.run_adb_cmd('push', src_quoted, dst_path, timeout=30)
            if result and str(file_size) in result:
                return result
            if result and 'No such file or directory' in result:
                logger.error(f"File not found: {src_path}")
                break
            logger.warning(f"Push attempt {attempt + 1} failed, retrying...")
        
        logger.error(f"Push file failed after {retries} attempts: {src_path}")
        return None

    def pull_file(self, src_path: str, dst_path: str) -> str | None:
        """从设备拉取文件
        
        :param src_path: 设备文件路径
        :param dst_path: 本地保存路径
        :return: 命令执行结果
        """
        result = self.run_adb_cmd('pull', src_path, dst_path, timeout=180)
        if result and 'failed to copy' in result:
            logger.error(f"Failed to pull file: {src_path}")
        return result

    def pull_files_by_time(self, src_dir: str, dst_dir: str, start_ts: float, end_ts: float) -> None:
        """拉取指定时间范围内的文件
        
        :param src_dir: 设备源目录
        :param dst_dir: 本地目标目录
        :param start_ts: 开始时间戳
        :param end_ts: 结束时间戳
        """
        dst_path = Path(dst_dir) / src_dir.split("/")[-1]
        dst_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in self.list_files_by_time(src_dir, start_ts, end_ts):
            self.pull_file(file_path, str(dst_path))

    def screenshot(self, save_path: str, use_exec_out: bool = False) -> str | None:
        """截图
        
        :param save_path: 保存路径
        :param use_exec_out: 是否使用 exec-out 直接输出到 PC
        :return: 命令执行结果
        """
        if use_exec_out:
            return self.run_adb_cmd(f'exec-out screencap -p {save_path}', timeout=20)
        return self.run_shell_cmd(f'screencap -p {save_path}', timeout=20)

    def remove(self, path: str, recursive: bool = False) -> str | None:
        """删除文件或目录
        
        :param path: 目标路径
        :param recursive: 是否递归删除
        :return: 命令执行结果
        """
        flag = '-R' if recursive else ''
        return self.run_shell_cmd(f'rm {flag} {path}'.strip())

    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在
        
        :param path: 目标路径
        :return: 是否存在
        """
        result = self.run_shell_cmd(f'ls -l {path}')
        if not result:
            return False
        return 'No such file or directory' not in result

    def mkdir(self, path: str) -> str | None:
        """创建目录
        
        :param path: 目录路径
        :return: 命令执行结果
        """
        return self.run_shell_cmd(f'mkdir -p {path}')

    def list_dir(self, path: str) -> list[str]:
        """列出目录内容
        
        :param path: 目录路径
        :return: 文件名列表
        """
        result = self.run_shell_cmd(f'ls -l {path}')
        if not result or 'No such file or directory' in result:
            return []
        
        files = []
        for line in result.replace('\r\r\n', '\n').split('\n'):
            parts = line.split()
            # 跳过 total 行和空行
            if len(parts) > 2 and parts[0] != "total":
                files.append(parts[-1])
        return files

    def list_files_by_time(self, path: str, start_ts: float, end_ts: float) -> list[str]:
        """列出指定时间范围内的文件
        
        :param path: 目录路径
        :param start_ts: 开始时间戳
        :param end_ts: 结束时间戳
        :return: 文件路径列表
        """
        result = self.run_shell_cmd(f'ls -l {path}')
        if not result or 'No such file or directory' in result:
            return []
        
        files = []
        time_pattern = re.compile(r'\S+\s+(\d+-\d+-\d+\s+\d+:\d+)\s+\S+')
        
        for line in result.replace('\r\r\n', '\n').split('\n'):
            match = time_pattern.search(line)
            if not match:
                continue
            
            modify_time = match.group(1)
            modify_ts = TimeUtils.getTimeStamp(modify_time, "%Y-%m-%d %H:%M")
            
            if start_ts < modify_ts < end_ts:
                filename = line.split()[-1]
                files.append(f'{path}/{filename}')
                logger.debug(f"Matched file: {filename}")
        
        return files

    def is_older_than(self, path: str, days: int = 7) -> bool:
        """检查文件是否超过指定天数
        
        :param path: 文件路径
        :param days: 天数阈值
        :return: 是否超过
        """
        result = self.run_shell_cmd(f'ls -l {path}')
        if not result or 'No such file or directory' in result:
            return False
        
        time_pattern = re.compile(r'\S+\s+(\d+-\d+-\d+\s+\d+:\d+)\s+\S+')
        match = time_pattern.search(result)
        
        if not match:
            return False
        
        modify_time = match.group(1)
        modify_ts = TimeUtils.getTimeStamp(modify_time, "%Y-%m-%d %H:%M")
        threshold_ts = time.time() - days * 24 * 60 * 60
        
        is_old = modify_ts < threshold_ts
        logger.debug(f"{path} is {'older' if is_old else 'newer'} than {days} days")
        return is_old

    def get_disk_usage(self, path: str) -> dict[str, int] | None:
        """获取目录磁盘使用情况
        
        :param path: 目录路径
        :return: 使用情况字典 {used_percent, used, available}
        """
        result = self.run_shell_cmd(f'df {path}')
        if not result:
            return None
        
        lines = result.replace('\r', '').splitlines()
        if len(lines) < 2:
            return None
        
        parts = lines[1].split()
        if len(parts) < 5:
            return None
        
        return {
            'used_percent': int(parts[4].replace('%', '')),
            'used_kb': int(parts[2]),
            'available_kb': int(parts[3])
        }

    # ==================== Activity 操作 ====================

    def start_activity(
        self, 
        activity: str, 
        action: str = '', 
        data_uri: str = '', 
        extras: dict | None = None,
        wait: bool = True,
        timeout: int = 30
    ) -> dict[str, str]:
        """启动 Activity
        
        :param activity: Activity 完整名称 (package/activity)
        :param action: Intent action
        :param data_uri: Data URI
        :param extras: 额外参数字典
        :param wait: 是否等待启动完成
        :param timeout: 超时时间
        :return: 启动结果字典
        """
        extras = extras or {}
        
        # 构建命令参数
        args = []
        if wait:
            args.append('-W')
        if action:
            args.append(f'-a {action}')
        if data_uri:
            args.append(f'-d {data_uri}')
        for key, value in extras.items():
            args.append(f'-e {key} {value}')
        
        cmd = f"am start {' '.join(args)} -n {activity}".strip()
        result = self.run_shell_cmd(cmd, timeout=timeout, retry=1)
        
        # 解析结果
        ret = {}
        for line in (result or '').split('\n'):
            if ': ' in line:
                key, _, value = line.partition(': ')
                ret[key.strip()] = value.strip()
        return ret

    def get_current_activity(self) -> str | None:
        """获取当前前台 Activity
        
        根据 SDK 版本选择最优方法
        """
        # Android 8.0+ 优先使用 usagestats
        if self.get_sdk_version() >= 26:
            methods = [self._get_activity_via_usagestats, self._get_activity_via_top]
        else:
            methods = [self._get_activity_via_top, self._get_activity_via_usagestats]
        
        for method in methods:
            activity = method()
            if activity:
                return activity
        return None

    def get_foreground_package(self) -> str | None:
        """获取当前前台应用包名"""
        activity = self.get_current_activity()
        if activity and '/' in activity:
            return activity.split('/')[0]
        return activity

    def _get_activity_via_window(self) -> str | None:
        """通过 dumpsys window 获取 Activity"""
        result = self.run_shell_cmd('dumpsys window windows')
        if not result:
            return None
        
        for line in result.split('\n'):
            if 'mCurrentFocus' not in line:
                continue
            
            # 解析: mCurrentFocus=Window{... u0 package/activity}
            parts = line.strip().split()
            if len(parts) < 2:
                return None
            
            # 找到 u0 后的部分，或直接使用第二部分
            if len(parts) > 2 and parts[1] == 'u0':
                activity = parts[2].rstrip('}')
            else:
                activity = parts[1].rstrip('}')
            
            logger.debug(f"Window focus activity: {activity}")
            return activity
        return None

    def _get_activity_via_top(self) -> str | None:
        """通过 dumpsys activity top 获取 Activity"""
        result = self.run_shell_cmd("dumpsys activity top")
        if not result:
            return None
        
        for line in result.split('\n'):
            if 'ACTIVITY' not in line:
                continue
            
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            
            activity_info = parts[1]
            # 处理不同格式
            if '/' in activity_info:
                if activity_info.endswith('/'):
                    activity = activity_info.rstrip('/')
                else:
                    activity = activity_info
            else:
                activity = activity_info
            
            logger.debug(f"Activity top: {activity}")
            return activity
        return None

    def _get_activity_via_usagestats(self) -> str | None:
        """通过 dumpsys usagestats 获取 Activity"""
        result = self.run_shell_cmd("dumpsys usagestats")
        if not result:
            return None
        
        # 找最后一个 MOVE_TO_FOREGROUND 事件
        last_line = ""
        for line in result.split('\n'):
            if 'MOVE_TO_FOREGROUND' in line:
                last_line = line.strip()
        
        if not last_line:
            return None
        
        # 解析 class=xxx
        if 'class=' not in last_line:
            return None
        
        activity = last_line.split('class=')[1].split()[0]
        logger.debug(f"UsageStats activity: {activity}")
        return activity

    # ==================== 进程管理 ====================
    
    def get_pid(self, package: str) -> int | None:
        """获取应用主进程 PID
            
        :param package: 应用包名
        :return: 进程 PID
        """
        processes = self.get_processes_by_name(package)
        return processes[0]['pid'] if processes else None
    
    def get_processes_by_name(self, name: str) -> list[dict]:
        """获取指定名称的进程列表
            
        :param name: 进程名/包名
        :return: 进程信息列表
        """
        return [p for p in self.list_processes() if p['name'] == name]
    
    def list_processes(self) -> list[dict]:
        """获取进程列表
            
        :return: 进程信息列表
        """
        # Android 8.0+ (API 26) 使用 ps -A
        cmd = 'ps -A' if self.get_sdk_version() >= 26 else 'ps'
        result = self.run_shell_cmd(cmd)
            
        if not result:
            return []
            
        lines = result.replace('\r', '').split('\n')
        if not lines:
            return []
            
        # 检测是否是 busybox 格式
        is_busybox = lines[0].startswith('PID')
        processes = []
            
        for line in lines[1:]:
            parts = line.split()
            if len(parts) < 5:
                continue
                
            try:
                if is_busybox:
                    proc = self._parse_busybox_process(parts)
                else:
                    proc = self._parse_standard_process(parts)
                    
                if proc:
                    processes.append(proc)
            except (ValueError, IndexError) as e:
                logger.debug(f"Failed to parse process line: {line}, error: {e}")
            
        return processes
    
    def _parse_standard_process(self, parts: list[str]) -> dict | None:
        """解析标准 ps 输出"""
        if len(parts) >= 9:
            return {
                'uid': parts[0],
                'pid': int(parts[1]),
                'ppid': int(parts[2]),
                'name': parts[8] if len(parts) > 8 else parts[7],
                'status': parts[-2]
            }
        elif len(parts) == 8:
            return {
                'uid': parts[0],
                'pid': int(parts[1]),
                'ppid': int(parts[2]),
                'name': parts[7],
                'status': parts[-2]
            }
        return None
    
    def _parse_busybox_process(self, parts: list[str]) -> dict | None:
        """解析 busybox ps 输出"""
        pid = int(parts[0])
            
        # 查找进程名索引
        idx = 4
        if len(parts) > idx and len(parts[idx]) == 1:
            idx += 1
        if len(parts) > idx and parts[idx].startswith('{') and parts[idx].endswith('}'):
            idx += 1
            
        name = parts[idx] if len(parts) > idx else ''
        ppid = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            
        return {
            'pid': pid,
            'uid': parts[1] if len(parts) > 1 else '',
            'ppid': ppid,
            'name': name,
            'status': parts[-2] if len(parts) > 2 else ''
        }
    
    def is_process_running(self, name: str) -> bool:
        """检查进程是否运行"""
        return any(p['name'] == name for p in self.list_processes())
    
    def kill_process(self, name: str) -> int:
        """杀死指定进程
            
        :param name: 进程名
        :return: 杀死的进程数
        """
        pids = [p['pid'] for p in self.get_processes_by_name(name)]
        if pids:
            self.run_shell_cmd(f"kill {' '.join(map(str, pids))}")
        return len(pids)
    
    def wait_process_exit(self, names: list[str], timeout: int = 10) -> bool:
        """等待进程退出
            
        :param names: 进程名列表
        :param timeout: 超时时间（秒）
        :return: 是否全部退出
        """
        start = time.time()
        while time.time() - start < timeout:
            running = {p['name'] for p in self.list_processes()}
            if not any(n in running for n in names):
                return True
            time.sleep(1)
        return False
    
    def dump_stack(self, pid: int, save_path: str) -> str | None:
        """导出进程堆栈
            
        :param pid: 进程 PID
        :param save_path: 保存路径
        """
        return self.run_shell_cmd(f"debuggerd -b {pid} > {save_path}")
    
    def dump_heap(self, package: str, save_dir: str) -> str | None:
        """导出 Java 堆
            
        :param package: 应用包名
        :param save_dir: 本地保存目录
        :return: 本地文件路径
        """
        timestamp = TimeUtils.getCurrentTimeUnderline()
        device_path = f"/data/local/tmp/{package}_dumpheap_{timestamp}.hprof"
            
        self.run_shell_cmd(f"am dumpheap {package} {device_path}")
        time.sleep(10)
            
        local_path = Path(save_dir) / f"{package}_dumpheap_{timestamp}.hprof"
        self.pull_file(device_path, str(local_path))
        return str(local_path)
    
    # ==================== 应用管理 ====================
    
    def clear_app_data(self, package: str) -> str | None:
        """清除应用数据"""
        return self.run_shell_cmd(f"pm clear {package}")
    
    def force_stop(self, package: str) -> str | None:
        """强制停止应用"""
        return self.run_shell_cmd(f"am force-stop {package}")
    
    def is_app_installed(self, package: str) -> bool:
        """检查应用是否安装"""
        return package in self.list_installed_apps()
    
    def list_installed_apps(self) -> list[str]:
        """获取已安装应用列表"""
        result = self.run_shell_cmd('pm list packages')
        if not result:
            return []
            
        apps = []
        for line in result.replace('\r', '').splitlines():
            if line.startswith('package:'):
                apps.append(line.split(':')[1])
            
        logger.debug(f"Found {len(apps)} installed apps")
        return apps
    
    def get_app_uid(self, package: str) -> str | None:
        """获取应用 UID
            
        优先从 packages.list 获取，失败则使用 dumpsys
        """
        # 方法1: 从 packages.list 获取
        result = self.run_shell_cmd('cat /data/system/packages.list')
        if result:
            for line in result.replace('\r\r\n', '\n').split('\n'):
                parts = line.split()
                if len(parts) >= 2 and parts[0] == package:
                    return parts[1]
            
        # 方法2: 从 dumpsys 获取
        result = self.run_shell_cmd(f'dumpsys package {package}')
        if result and 'Unable to find package:' not in result:
            match = re.search(r'userId=(\d+)', result)
            if match:
                uid = match.group(1)
                logger.debug(f"UID for {package}: {uid}")
                return uid
            
        return None
    
    def install_apk(self, apk_path: str, reinstall: bool = True, downgrade: bool = False) -> bool:
        """安装 APK
            
        :param apk_path: APK 路径
        :param reinstall: 是否覆盖安装
        :param downgrade: 是否允许降级
        :return: 是否成功
        """
        apk = Path(apk_path)
        if not apk.exists():
            logger.error(f"APK not found: {apk_path}")
            return False
            
        # 推送到设备
        tmp_path = f"/data/local/tmp/{apk.name}"
        if not self.push_file(apk_path, tmp_path):
            return False
            
        # 构建安装命令
        flags = []
        if reinstall:
            flags.extend(['-r', '-t'])
        if downgrade:
            flags.append('-d')
            
        cmd = f"pm install {' '.join(flags)} {tmp_path}".strip()
            
        # 重试安装
        for attempt in range(3):
            result = self.run_shell_cmd(cmd, timeout=180, retry=1)
            logger.debug(f"Install attempt {attempt + 1}: {result}")
                
            if 'Success' in result:
                return True
            if 'INSTALL_FAILED_ALREADY_EXISTS' in result:
                if reinstall:
                    return True
                # 尝试卸载后重装
                return self.install_apk(apk_path, reinstall=False, downgrade=downgrade)
            if 'INSTALL_PARSE_FAILED_INCONSISTENT_CERTIFICATES' in result:
                return self.install_apk(apk_path, reinstall=False, downgrade=False)
            if 'INSTALL_FAILED_INSUFFICIENT_STORAGE' in result:
                raise RuntimeError(f"Insufficient storage: {result}")
            
        logger.error(f"Install failed after retries: {result}")
        return False
    
    def uninstall_apk(self, package: str) -> bool:
        """卸载应用
            
        :param package: 应用包名
        :return: 是否成功
        """
        result = self.run_adb_cmd('uninstall', package, timeout=30)
        return result is not None and 'Success' in result
    
    # ==================== 设备信息 ====================
    
    def get_system_version(self) -> str | None:
        """获取系统版本 (如 4.1.2)"""
        if self._system_version is None:
            self._system_version = self.run_shell_cmd("getprop ro.build.version.release")
        return self._system_version
    
    def get_sdk_version(self) -> int | None:
        """获取 SDK 版本"""
        if self._sdk_version is None:
            result = self.run_shell_cmd('getprop ro.build.version.sdk')
            self._sdk_version = int(result) if result and result.isdigit() else None
        return self._sdk_version
    
    def get_brand(self) -> str | None:
        """获取设备品牌"""
        if self._phone_brand is None:
            self._phone_brand = self.run_shell_cmd('getprop ro.product.brand')
        return self._phone_brand
    
    def get_model(self) -> str | None:
        """获取设备型号"""
        if self._phone_model is None:
            self._phone_model = self.run_shell_cmd('getprop ro.product.model')
        return self._phone_model
    
    def get_cpu_abi(self) -> str | None:
        """获取 CPU 架构"""
        return self.run_shell_cmd('getprop ro.product.cpu.abi')
    
    def get_imei(self) -> str | None:
        """获取设备 IMEI"""
        result = self.run_shell_cmd('dumpsys iphonesubinfo')
        if not result:
            return None
            
        for line in result.replace('\r\r\n', '\n').split('\n'):
            if 'Device ID' in line and '=' in line:
                return line.split('=')[1].strip()
            
        logger.error(f"Failed to get IMEI: {result[:100]}")
        return None
    
    def get_screen_resolution(self) -> str | None:
        """获取屏幕分辨率"""
        return self.run_shell_cmd('wm size')
    
    # ==================== 其他操作 ====================
    
    def input_text(self, text: str) -> str | None:
        """输入文本"""
        return self.run_shell_cmd(f"input text '{text}'")
    
    def ping(self, host: str, count: int = 4) -> str | None:
        """Ping 测试"""
        return self.run_shell_cmd(f"ping -c {count} {host}", timeout=count * 2 + 5)
    
    def forward_port(self, local_port: int, remote_port: int, proto: str = 'tcp') -> bool:
        """端口转发
            
        :param local_port: 本地端口
        :param remote_port: 远程端口
        :param proto: 协议类型 (tcp/localabstract)
        :return: 是否成功
        """
        result = self.run_adb_cmd('forward', f'tcp:{local_port}', f'{proto}:{remote_port}')
        return result is not None
    
    def reboot(self, mode: str | None = None) -> str | None:
        """重启设备
            
        :param mode: 重启模式 (bootloader/recovery/None)
        """
        if mode:
            return self.run_adb_cmd('reboot', mode)
        return self.run_adb_cmd('reboot')


class AndroidDevice:
    """Android 设备封装类
    
    提供设备连接管理和 ADB 操作入口
    """
    
    # 远程设备模式匹配: hostname:serialNumber
    _REMOTE_PATTERN = re.compile(r'([\w\-\.]+):(.+)')

    def __init__(self, device_id: str | None = None):
        self.device_id = device_id
        self.is_local = self._is_local_device(device_id)
        self.adb: ADB | None = ADB(device_id) if self.is_local else None

    @staticmethod
    def _is_local_device(device_id: str | None) -> bool:
        """判断是否为本地设备
        
        本地真机: serialNumber
        本地模拟器: hostname:portNumber (端口范围 1024-65536)
        远程设备: hostname:serialNumber
        """
        if not device_id:
            return True
        
        match = AndroidDevice._REMOTE_PATTERN.match(device_id)
        if not match:
            return True
        
        # 如果是端口号格式，则是本地模拟器
        port_part = match.group(2)
        return port_part.isdigit() and 1024 < int(port_part) < 65536

    @staticmethod
    def list_devices() -> list[str]:
        """获取已连接的设备列表"""
        return ADB.list_devices()

    def is_connected(self) -> bool:
        """检查设备是否已连接"""
        return self.adb is not None and self.adb.is_connected()


# ==================== 测试入口 ====================

def cleanup_old_results(results_dir: str, days: int = 3) -> int:
    """清理过期结果文件
    
    :param results_dir: 结果目录
    :param days: 过期天数
    :return: 清理的文件数
    """
    import shutil
    
    path = Path(results_dir)
    if not path.exists():
        return 0
    
    cutoff_time = time.time() - days * 24 * 60 * 60
    count = 0
    
    for item in path.iterdir():
        try:
            if item.stat().st_ctime < cutoff_time:
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
                count += 1
                logger.debug(f"Removed: {item}")
        except Exception as e:
            logger.warning(f"Failed to remove {item}: {e}")
    
    return count


if __name__ == '__main__':
    # 示例: 列出设备
    devices = AndroidDevice.list_devices()
    print(f"Connected devices: {devices}")
    
    # 示例: 清理旧结果
    # cleanup_old_results("/path/to/results", days=3)
