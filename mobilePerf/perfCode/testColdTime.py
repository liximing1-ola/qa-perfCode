import os
import time


# 测试冷启动时间
# 创建App进程, 加载相关资源, 启动Main Thread, 初始化首屏Activity
def startUpTime(device, pg_name, pga_name):
    """
    :param device: 设备id
    :param pg_name: activity名称
    :param pga_name: 包名
    """
    wait_time = 5
    try:
        with open('E:/report/coldStartUp.txt', 'wb+') as file:
            su_time = []
            for i in range(30):
                os.popen("adb -s {} shell am force-stop {}".format(device, pg_name))  # kill 进程
                time.sleep(wait_time)
                # 启动activity
                start = os.popen("adb -s {} shell am start -W {}".format(device, pga_name))
                time.sleep(wait_time)
                data = start.readlines()
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        print("TotalTime为: {}ms".format(line[11:]))
                        if int(line[11:]) == 0:
                            break
                        su_time.append(int(line[11:]))
                        file.write(('第{}次\n'.format(i + 1)).encode())
                        line += '\n'
                        line = line.encode()
                        file.write(line)
            return su_time
    except os.error as error:
        print(error)


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


def main_cold():
    # 取测试机-s
    s = getDev()
    pn = 'com.imbb.banban.android'
    an = 'com.imbb.banban.android/.MainActivity'  # aapt dump badging + apk
    print('设备id：{}, APP包名：{}, activity：{}'.format(s, pn, an))
    time_list = startUpTime(s, pn, an)
    total_time = 0
    for i in time_list:
        total_time += i
    avg_time = total_time / len(time_list)
    print('冷启动平均耗时： {}ms'.format(avg_time))


if __name__ == '__main__':
    main_cold()
