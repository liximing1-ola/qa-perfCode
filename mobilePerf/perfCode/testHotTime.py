import os
import time


def hotTime(device, pg_name, pga_name):
    """
    :param device:
    :param pg_name:
    :param pga_name:
    :return:
    """
    # kill 进程
    wait_time = 5
    os.popen("adb -s {} shell am force-stop {}".format(device, pg_name))
    time.sleep(wait_time)
    os.popen("adb -s {} shell am start -W {}".format(device, pga_name))
    time.sleep(wait_time)
    try:
        with open('E:/report/hotTime.txt', 'wb+') as f:
            hot_time = []
            for i in range(30):
                keyEvent(3)  # Home
                time.sleep(wait_time)
                start = os.popen("adb -s {} shell am start -W {}".format(device, pga_name))  # 启动activity
                time.sleep(wait_time)
                data = start.readlines()
                for line in data:
                    if "TotalTime:" in line:
                        line = line.strip()
                        print("TotalTime为:{}ms".format(line[11:]))
                        if int(line[11:]) == 0:
                            break
                        hot_time.append(int(line[11:]))
                        f.write(('第{}次\n'.format(i + 1)).encode())
                        line += '\n'
                        f.write(line.encode())
            return hot_time
    except os.error as error:
        print(error)


# 获得设备ID
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


# 模拟发送keyEvent
def keyEvent(keycode):
    """
    :param keycode: 键值
    """
    # KEYCODE_HOME = 3
    # KEYCODE_BACK = 4
    cmd = 'adb shell input keyevent {}'.format(keycode)
    os.popen(cmd)
    time.sleep(1)


def main_hot():
    """
    :return:
    """
    s = getDev()
    pn = 'com.imbb.banban.android'
    an = 'com.imbb.banban.android/.MainActivity'  # aapt dump badging + apk
    print(s, pn, an)
    hot_list = hotTime(s, pn, an)
    print(sum(hot_list) / len(hot_list))


if __name__ == '__main__':
    main_hot()
