import os
import time


# 测试启动时间
# 创建App进程, 加载相关资源, 启动Main Thread, 初始化首屏Activity
class testPhoneTime:
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

    def startHotTime(self):
        os.popen("adb -s {} shell am force-stop {}".format(self.device, self.pg_name))
        time.sleep(self.wait_time)
        os.popen("adb -s {} shell am start -W {}".format(self.device, self.pga_name))
        time.sleep(self.wait_time)
        try:
            hot_time = []
            for i in range(30):
                testPhoneTime.keyEvent(3)  # Home
                time.sleep(self.wait_time)
                start = os.popen("adb -s {} shell am start -W {}".format(self.device, self.pga_name))
                time.sleep(self.wait_time)
                data = start.readlines()
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        print("TotalTime为:{}ms".format(line[11:]))
                        if int(line[11:]) == 0:
                            break
                        hot_time.append(int(line[11:]))
            return hot_time
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

    @staticmethod
    def keyEvent(keycode):
        """
        :param keycode: 键值
        """
        # KEYCODE_HOME = 3
        # KEYCODE_BACK = 4
        cmd = 'adb shell input keyevent {}'.format(keycode)
        os.popen(cmd)
        time.sleep(1)

    @staticmethod
    def main(mode):
        # 包名：activity名
        # aapt dump badging + apk
        pn = 'com.imbb.banban.android'
        an = 'com.imbb.banban.android/.MainActivity'
        print('设备id：{}, APP包名：{}, activity：{}'.format(testPhoneTime.getDev(), pn, an))
        testTime = testPhoneTime(device=testPhoneTime.getDev(), pg_name=pn, pga_name=an)
        if mode == 'cold':
            time_list = testTime.startUpTime()
        elif mode == 'hot':
            time_list = testTime.startHotTime()
        else:
            raise Exception('again')
        print(time_list)
        print('去掉最高值：{}'.format(max(time_list)))
        print('去掉最低值：{}'.format(min(time_list)))
        time_list.remove(max(time_list))
        time_list.remove(min(time_list))
        avg_time = int(sum(time_list) / len(time_list))
        print('{}启动平均耗时: {}ms'.format(mode, avg_time))


if __name__ == '__main__':
    testPhoneTime.main('cold')  # 冷启动
    testPhoneTime.main('hot')  # 热启动
