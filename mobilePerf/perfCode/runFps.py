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
        if not dev:  # Check if device is available
            return '未找到有效设备'

        cmd = f'adb -s {dev} shell dumpsys window w | findstr / | findstr name='
        context = os.popen(cmd)
        data = context.readlines()

        # Simplified package name extraction with loop
        target_activity = 'com.x.x.android.MainActivity'
        pattern = re.compile(r'\((.*?)/', re.S)  # Reusable regex pattern

        for line in data:
            if target_activity in line:
                match = pattern.search(line)
                if match:
                    # Extract package name (handles different offsets with split)
                    return match.group(1).split()[-1]

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
        # Use regex for reliable device ID extraction
        result = os.popen('adb devices').read()
        match = re.search(r'^(\S+)\s+device$', result, re.MULTILINE)
        if match:
            return match.group(1)  # Return first connected device
        return None  # No valid device found
    except Exception as error:
        print(f"获取设备ID失败: {error}")
        return None


def Fps():
    device_id = getDev()
    if not device_id:
        print("未找到连接的设备,无法执行操作")
        return

    print(f'当前设备id: {device_id}')
    i = 1
    # Define swipe sequences as constants
    SWIPE_SEQ1 = [
        'input swipe 100 550 100 100 50',
        'input swipe 200 600 200 200 100',
        'input swipe 500 500 200 200 100'
    ]
    SWIPE_SEQ2 = [
        'input swipe 400 250 360 100 150',
        'input swipe 500 720 400 500 150'
    ]

    while i <= 2000:
        # Randomly choose sequence and execute swipes
        if random.randint(1, 2) == 1:
            swipe_list = SWIPE_SEQ1
        else:
            swipe_list = SWIPE_SEQ2

        # Execute up to 20 swipes with loop control
        for _ in range(20):
            if i > 2000:
                break
            s = random.choice(swipe_list)
            adb_cmd = f'adb -s {device_id} shell {s}'
            os.system(adb_cmd)
            i += 1
            print(f'{device_id}: {adb_cmd}, i={i}')
            time.sleep(0.05)


if __name__ == '__main__':
    Fps()
