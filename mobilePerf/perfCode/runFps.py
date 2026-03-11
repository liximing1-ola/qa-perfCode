import os
import re
import time
import random


def getPackageName():
    """
    :return: 获得包名
    """
    try:
        dev = getDev()
        cmd = 'adb -s {} shell dumpsys window w |findstr \/ |findstr name='.format(dev)
        context = os.popen(cmd)
        data = context.readlines()
        if 'com.imbb.banban.android.MainActivity' in data[0] and len(data) >= 1:
            r = re.compile(r'[(](.*?)[/]', re.S)
            return (re.findall(r, data[0]))[0][5:]
        elif len(data) >= 4 and 'com.imbb.banban.android.MainActivity' in data[3]:
            r = re.compile(r'[(](.*?)[/]', re.S)
            return (re.findall(r, data[3]))[0][5:]
        elif len(data) >= 6 and 'com.imbb.banban.android.MainActivity' in data[5]:
            r = re.compile(r'[(](.*?)[/]', re.S)
            return (re.findall(r, data[5]))[0][13:]
        return '取不到包名,请先启动应用or重启应用'
    except EnvironmentError as error:
        print('请用USB连接设备', error)
    except Exception as error:
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


def Fps():
    print('当前设备id: {}'.format(getDev()))
    i = 1
    while i <= 2000:
        r = random.randint(1, 2)
        if r == 1:
            m = 1
            while m <= 20:
                swipe_list = ['adb shell input swipe 100 550 100 100 50',
                              'adb shell input swipe 200 600 200 200 100',
                              'adb shell input swipe 500 500 200 200 100']
                s = random.choice(swipe_list)
                os.system(s)
                m += 1
                i += 1
                print('{}: {}, m={}, i={}'.format(getDev(), s, m, i))
                time.sleep(0.05)
        elif r == 2:
            n = 1
            while n <= 20:
                swipe_list = ['adb shell input swipe 400 250 360 100 150',
                              'adb shell input swipe 500 720 400 500 150']
                s = random.choice(swipe_list)
                os.system(s)
                n += 1
                i += 1
                print('{}: {}, n={}, i={}'.format(getDev(), s, n, i))
                time.sleep(0.05)


if __name__ == '__main__':
    Fps()
