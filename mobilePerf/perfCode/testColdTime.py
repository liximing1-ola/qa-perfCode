import os
import time


# 测试冷启动时间
# 创建App进程, 加载相关资源, 启动Main Thread, 初始化首屏Activity
class testColdTime:
    def __init__(self, device, pg_name, pga_name):
        self.wait_time = 5  # 间隔时间
        self.device = device  # 设备序列号
        self.pg_name = pg_name  # 包名
        self.pga_name = pga_name  # activity名

    def startUpTime(self):
        try:
            su_time = []
            for i in range(30):
                os.popen("adb -s {} shell am force-stop {}".format(self.device, self.pg_name))  # kill 进程
                time.sleep(self.wait_time)
                start = os.popen("adb -s {} shell am start -W {}".format(self.device, self.pga_name))
                time.sleep(self.wait_time)
                data = start.readlines()
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        print("TotalTime为: {}ms".format(line[11:]))
                        if int(line[11:]) == 0:
                            break
                        su_time.append(int(line[11:]))
                        # file.write(('第{}次\n'.format(i + 1)).encode())
                        # line += '\n'
                        # line = line.encode()
                        # file.write(line)
            return su_time
        except os.error as error:
            print(error)

    @staticmethod
    def getDev():
        """
        :return: 获得设备id
        """
        try:
            devices_info = os.popen('adb devices')
            data = devices_info.readlines()
            if len(data) != 0 and data[1].find('device'):
                s = data[1][:-8]
                return s
            return 0
        except Exception as error:
            print(error)


if __name__ == '__main__':
    # 包名：activity名
    pn = 'com.imbb.banban.android'
    an = 'com.imbb.banban.android/.MainActivity'  # aapt dump badging + apk
    # TT语音
    # pn = 'com.yiyou.ga'
    # an = 'com.yiyou.ga/com.yiyou.ga.client.BlankActivity'
    print('设备id：{}, APP包名：{}, activity：{}'.format(testColdTime.getDev(), pn, an))

    testTime = testColdTime(device=testColdTime.getDev(), pg_name=pn, pga_name=an)
    time_list = testTime.startUpTime()
    print(time_list)
    total_time = 0
    for i in time_list:
        total_time += i
    avg_time = int(total_time / len(time_list))
    print('冷启动平均耗时： {}ms'.format(avg_time))
