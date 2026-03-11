import csv
import traceback
from pylab import *
import os

BaseDir = os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))
from mobilePerf.perfCode.common.config import config
from mobilePerf.perfCode.androidDevice import AndroidDevice
from mobilePerf.perfCode.common.utils import TimeUtils, FileUtils
from mobilePerf.perfCode.common.log import logger
from mobilePerf.perfCode.globaldata import RuntimeData


class PckCpuInfo(object):
    """
    使用top 直接进行统计.top中的数值基本上是瞬时值，采样的数据也是来自于/proc/pid/stat(具体进程的cpu%)
    """
    # 1:cpu   2:user   3:nice  4:sys  5:idle     6:iow  7:irq    8:sirq   9:host
    # 400%cpu  56%user   1%nice  46%sys 285%idle   0%iow  10%irq   2%sirq   0%host
    # User 0%, System 0%, IOW 0%, IRQ 0%

    RE_CPU = re.compile(r'User (\d+)\%\, System (\d+)\%\, IOW (\d+)\%\, IRQ (\d+)\%')
    RE_CPU_O = re.compile(
        r'(\d+)\%cpu\s+(\d+)\%user\s+(\d+)\%nice\s+(\d+)\%sys\s+(\d+)\%idle\s+(\d+)\%iow\s+(\d+)\%irq\s+(\d+)\%sirq\s+(\d+)\%host')

    def __init__(self, packages, source, sdkVersion):
        """
        :param packages: 应用的包名
        :param source: 数据源，来自于adb shell top.
        """
        self.source = source
        self.sdkVersion = sdkVersion
        self.datetime = ''
        self.packages = packages
        self.pid = 0
        self.uid = ''
        self.pck_cpu_rate = ''
        self.pck_pyc = ''
        self.uid_cpu_rate = ''
        self.package_list = []
        self.device_cpu_rate = ''  # 整机的cpu使用率
        self.system_rate = ""
        self.user_rate = ''
        self.nice_rate = ''
        self.idle_rate = ''
        self.iow_rate = ''
        self.irq_rate = ''
        self.total_pid_cpu = 0
        self._parse_cpu_usage()
        self._parse_package()

    def _parse_package(self):
        """
        解析top命令中的包的cpu信息
        :return:
        """
        if self.packages is None or self.packages == "":
            logger.error("no process name input, please input")

        for package in self.packages:
            package_dic = {"package": package, "pid": "", "pid_cpu": ""}
            sp_lines = self.source.split('\n')
            for line in sp_lines:
                if package in line:  # 解析进程cpu信息
                    tmp = line.split()
                    self.pid = tmp[0]
                    target_pck = tmp[-1]  # 解析包名
                    self.datetime = TimeUtils.getCurrentTime()
                    if package == target_pck:  # 只统计包名一致的Process
                        if int(self.pid) > 0:
                            logger.debug(
                                "cpuinfos, into _parse_pck packege is target package, pid is :" + str(self.pid))
                            cpu_index = self.get_cpucol_index()
                            uid_index = self.get_uidcol_index()
                            if len(tmp) > cpu_index:
                                self.pck_cpu_rate = tmp[cpu_index]
                                # CPU% 9% 有的格式会有%
                                self.pck_cpu_rate = self.pck_cpu_rate.replace("%", "")
                            if len(tmp) > uid_index:
                                self.uid = tmp[uid_index]
                            package_dic = {"package": package, "pid": self.pid, "pid_cpu": str(self.pck_cpu_rate),
                                           "uid": self.uid}
                            # 将top中解析出来的信息保存在一个列表中，作为一条记录添加在package_list中
                            logger.debug("package: " + package + ", cpu_rate: " + str(self.pck_cpu_rate))
                            self.total_pid_cpu += float(self.pck_cpu_rate)
                        break
            self.package_list.append(package_dic)
            logger.debug(package_dic)

    def _parse_cpu_usage(self):
        """
        从top中解析出cpu的信息
        :return:
        """
        if self.sdkVersion < 26:  # 版本判断，处理Android8以上版本
            match = self.RE_CPU.search(self.source)
            if match:
                self.user_rate = match.group(1)
                self.system_rate = match.group(2)
                self.iow_rate = match.group(3)
                self.irq_rate = match.group(4)
                self.device_cpu_rate = int(self.user_rate) + int(self.system_rate)
                logger.debug(" cpuinfos, device system_rate: %s" % self.system_rate)
                logger.debug(" cpuinfos, device user_rate: %s" % self.user_rate)
                logger.debug(" cpuinfos, device device_cpu_rate: %s" % self.device_cpu_rate)
        else:  # android8以上版本
            #  1:cpu 2:user 3:nice 4:sys 5:idle 6:iow 7:irq 8:sirq 9:host
            match = self.RE_CPU_O.search(self.source)
            if match:
                self.user_rate = match.group(2)
                self.nice_rate = match.group(3)
                self.system_rate = match.group(4)
                self.idle_rate = match.group(5)
                self.iow_rate = match.group(6)
                self.irq_rate = match.group(7)
                self.device_cpu_rate = int(self.user_rate) + int(self.system_rate)
                logger.debug("android8.0 or higher, user_rate: " + str(self.user_rate) + ", sys: " + str(
                    self.system_rate) + ",device cpu: " + str(self.device_cpu_rate))
                logger.debug("idle_rate: %s" % self.idle_rate)

    def sum_procs_cpurate(self):
        """
        :return: 所有进程cpu%之和
        """
        summ = 0
        if self.source:
            sp_lines = self.source.split("\n")
            for line in sp_lines:
                if self.uid != "" and self.uid in line:  # 过滤 uid
                    tmp = line.split()
                    cpu_index = self.get_cpucol_index()
                    summ += int(tmp[cpu_index].replace("%", ""))
            self.uid_cpu_rate = str(summ) + "%"
            for i in range(len(self.package_list)):
                self.package_list[i].append(self.uid_cpu_rate)
                logger.debug("cpuinfos, sum_procs_cpurate , afer append uid cpu rate, the package list is : " + str(
                    self.package_list))

    def get_cpucol_index(self):
        """
        :return: cpu%所在的列标
        """
        return self.get_col_index(self.source, ["CPU]", "CPU%"], 2)

    def get_pcycol_index(self):
        """
        :return: top中pyc的列标
        """
        return self.get_col_index(self.source, ["PCY"], -1)

    def get_packagenamecol_index(self):
        """
        :return: top中的packagename的列标
        """
        return self.get_col_index(self.source, ["ARGS"], -1)

    def get_vsscol_index(self):
        return self.get_col_index(self.source, ["VSS"], -1)

    def get_rss_col_index(self):
        return self.get_col_index(self.source, ["RSS"], -1)

    def get_uidcol_index(self):
        """
        由于uid的列名在不同机器上会有差别，这里单独区分
        :return: adb shell top中uid列的列标
        """
        if self.source:
            sp_lines = self.source.split("\n")
            for line in sp_lines:
                if 'UID' in line:
                    line_sp = line.split()
                    for key, item in enumerate(line_sp):
                        if item == "UID":
                            return key
                elif 'USER' in line:
                    line_sp = line.split()
                    for key, item in enumerate(line_sp):
                        if item == "USER":
                            return key
        return 8

    def get_col_index(self, s, col_name_list, default):
        """
        返回top中列标的通用的方法
        :param s: 一条top命令的值
        :param col_name: 列名列表 可能会有不同格式
        :param default:默认返回的列标
        :return:
        """
        s = s.split("\n")
        if s:
            for line in s:
                line = line.strip()
                for col_name in col_name_list:
                    if col_name in line:
                        line_sp = re.split(r"\[%|\s+", line)
                        for key, item in enumerate(line_sp):
                            if item == col_name:
                                logger.debug('=========== item == col_name: ' + col_name + " index : " + str(key))
                                return key
        return default


class CpuCollector(object):
    """
    通过top命令搜集cpu信息的一个类
    """

    def __init__(self, device, packages, interval=1, timeout=24 * 60 * 60):
        """
        :param device: 具体的设备实例
        :param packages: 应用的包名列表
        :param interval: 数据采集的频率
        :param timeout: 采集的超时，超过这个时间，任务会停止采集,默认是24个小时
        """
        self.cpu_queue = None
        self.device = device
        self.packages = packages
        self._interval = interval
        self._timeout = timeout
        self._stop_event = threading.Event()
        self.cpu_list = []
        self.sdkversion = self.get_sdkversion()
        # top可能会有进程名显示不全的问题 加-b即可
        self.top_cmd = 'top -b -n 1 -d %d' % self._interval
        ret = self.device.adb.run_shell_cmd(self.top_cmd)
        if ret and 'Invalid argument "-b"' in ret:
            logger.debug("top -b not support")
            self.top_cmd = 'top -n 1 -d %d' % self._interval
        logger.debug("sdk version : " + str(self.sdkversion))

    def get_sdkversion(self):
        sdk = self.device.adb.get_sdk_version()
        if sdk is None:
            sdk = 25
        return sdk

    def start(self, start_time):
        """
        启动一个搜集器来启动一个新的线程搜集cpu信息
        :return:
        """
        self.collect_package_cpu_thread = threading.Thread(target=self._collect_package_cpu_thread, args=(start_time,))
        self.collect_package_cpu_thread.start()
        logger.debug("INFO: CpuCollector start...")

    def stop(self):
        """
        停止cpu的搜集器
        :return:
        """
        logger.debug("INFO: CpuCollector stop...")
        if self.collect_package_cpu_thread.isAlive():
            self._stop_event.set()
            self.collect_package_cpu_thread.join(timeout=2)
            self.collect_package_cpu_thread = None

        if hasattr(self, "_top_pipe"):
            if self._top_pipe.poll() is None:  # 查看top进程是否仍然存在，如果还存在，就结束掉
                self._top_pipe.terminate()

    def _top_cpuinfo(self):
        self._top_pipe = self.device.adb.run_shell_cmd(self.top_cmd, sync=False)
        out = self._top_pipe.stdout.read()
        error = self._top_pipe.stderr.read()
        if error:
            logger.error("into cpuinfos error : " + str(error))
            return
        out = str(out, "utf-8")
        out.replace('\r', '')
        top_file = os.path.join(RuntimeData.package_save_path, 'top.txt')
        with open(top_file, "a+", encoding="utf-8") as writer:
            writer.write(TimeUtils.getCurrentTime() + " top info:\n")
            writer.write(out + "\n\n")
        #  避免文件过大，超过100M清理
        if FileUtils.get_FileSize(top_file) > 100:
            os.remove(top_file)
        return PckCpuInfo(self.packages, out, self.sdkversion)

    def get_max_freq(self):
        out = self.device.adb.run_shell_cmd("cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq")
        out.replace('\r', '')
        max_freq_file = os.path.join(RuntimeData.package_save_path, 'scaling_max_freq.txt')
        with open(max_freq_file, "a+", encoding="utf-8") as writer:
            writer.write(TimeUtils.getCurrentTime() + " scaling_max_freq:\n")
            writer.write(out + "\n\n")

    def _collect_package_cpu_thread(self, start_time):
        """
        按照指定频率，循环搜集cpu的信息
        :return:
        """
        end_time = time.time() + self._timeout
        cpu_title = ["datetime", "device_cpu_rate%", "user%", "system%", "idle%"]
        cpu_file = os.path.join(RuntimeData.package_save_path, 'cpuInfo.csv')
        for i in range(0, len(self.packages)):
            cpu_title.extend(["package", "pid", "pid_cpu%"])
        if len(self.packages) > 1:
            cpu_title.append("total_pid_cpu%")
        try:
            with open(cpu_file, 'w+') as df:
                csv.writer(df, lineterminator='\n').writerow(cpu_title)
        except RuntimeError as e:
            logger.error(e)
        while not self._stop_event.is_set() and time.time() < end_time:
            try:
                logger.debug("---------------cpuinfos, into _collect_package_cpu_thread loop thread is : " + str(
                    threading.current_thread().name))
                before = time.time()
                # 为了cpu值的准确性，将采集的时间间隔放在top命令中了
                cpu_info = self._top_cpuinfo()
                after = time.time()
                time_consume = after - before
                # logger.info("  ============== time consume for cpu info : "+str(time_consume))
                if cpu_info is None or cpu_info.source == '' or not cpu_info.package_list:
                    logger.debug("cpuinfos, can't get cpu info, continue")
                    continue
                self.cpu_list.extend([TimeUtils.getCurrentTime(), str(cpu_info.device_cpu_rate), cpu_info.user_rate,
                                      cpu_info.system_rate, cpu_info.idle_rate])
                for i in range(0, len(self.packages)):
                    if len(cpu_info.package_list) == len(self.packages):
                        self.cpu_list.extend([cpu_info.package_list[i]["package"], cpu_info.package_list[i]["pid"],
                                              cpu_info.package_list[i]["pid_cpu"]])
                if len(self.packages) > 1:
                    self.cpu_list.append(cpu_info.total_pid_cpu)
                #  去掉top命令耗时时间，
                logger.info("INFO: CpuMonitor save cpu_device_list: " + str(self.cpu_list))
                try:
                    with open(cpu_file, 'a+', encoding="utf-8") as df:
                        csv.writer(df, lineterminator='\n').writerow(self.cpu_list)
                        del self.cpu_list[:]
                except RuntimeError as e:
                    logger.error(e)

                delta_inter = self._interval - time_consume
                if delta_inter > 0:
                    time.sleep(delta_inter)
            except Exception as e:
                logger.error("an exception hanpend in cpu thread , reason unkown!, e:")
                logger.error(e)
                s = traceback.format_exc()
                logger.debug(s)  # 打印log日志记录debug
                if self.cpu_queue:
                    self.cpu_queue.task_done()
        logger.debug("stop event is set or timeout")


class CpuMonitor(object):
    """
    cpu 监控器
    """

    def __init__(self, device_id, packages, interval=5, timeout=24 * 60 * 60):
        self.device = AndroidDevice(device_id)
        self.packages = packages
        self.cpu_collector = CpuCollector(self.device, packages, interval, timeout)

    def start(self, start_time):
        """
        启动CPU监控器，收集cpu数据信息
        :return:
        """
        if not RuntimeData.package_save_path:
            RuntimeData.package_save_path = os.path.join(os.path.abspath(os.path.join(os.getcwd(), "../..")), 'results',
                                                         self.packages[0])
            if not os.path.exists(RuntimeData.package_save_path):
                os.makedirs(RuntimeData.package_save_path)
        self.start_time = start_time
        self.cpu_collector.start(start_time)
        logger.debug("INFO: CpuMonitor has started...") # cpu，om

    def stop(self):
        self.cpu_collector.stop()
        logger.debug("INFO: CpuMonitor has stopped...")

    def _get_cpu_collector(self):
        return self.cpu_collector

    def save(self):
        pass


def csvToList(csv_path):
    y = []
    with open(csv_path, 'r+', encoding='utf-8') as f:
        for data_list in [i for i in csv.reader(f)][1:]:
            y.append(round(float(data_list[7])))
        return y


def chart_cpu(x, y, t, details):
    """
    :param x: X轴列表
    :param y: Y轴列表
    :param t: 图片Name
    :param details: Title详情
    """
    try:
        if y and len(x) == len(y):
            plt.plot(x, y)
            plt.xlabel('Time(Min)', color='r')
            plt.ylabel('CPU(*%)', color='r')
            plt.title(t, color='g')
            plt.grid(True)
            plt.savefig('E:/report/{}.png'.format(details))
            plt.show()
        else:
            raise Exception(' x != y')
    except Exception as error:
        print(error)


def main_cpu(num):
    monitor = CpuMonitor(config.deviceId, [config.package], 20)
    monitor.start(TimeUtils.getCurrentTimeUnderline())
    time.sleep(20 * num)  # 执行时间  执行后查看当前数据是否符合预期
    monitor.stop()


def main_chart():
    # csv_path = BaseDir + '/results/' + config.package + '/cpuInfo.csv'
    csv_path = 'E:/mobileperf/results/com.imbb.banban.android/cpuInfo.csv'
    y = csvToList(csv_path)
    if len(y) == 30:
        chart_cpu(range(1, 31), y, 'chatroom-CPU ', 'banban')


if __name__ == "__main__":
    main_chart()
    # main_cpu(30)
