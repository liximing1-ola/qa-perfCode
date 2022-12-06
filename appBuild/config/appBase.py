import os
import re


class base:
    def __init__(self):
        self.base_path = 'D:/build-tools/build-tools/29.0.2'  # 本地路径
        self.aapt_path = os.path.join(self.base_path, 'aapt.exe')

    def getAppInfo(self, apk_path):
        base._checkPath(self.base_path)
        get_info_command = "{} dump badging {}".format(self.aapt_path, apk_path)
        output = os.popen(get_info_command)
        output = output.buffer.read().decode(encoding='utf-8')
        match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(output)
        if not match:
            print(output)
            raise Exception("can't get packageInfo")
        packageName = match.group(1)
        versionCode = match.group(2)
        versionName = match.group(3)
        print(" 包名：%s \n 版本号：%s \n 版本名称：%s " % (packageName, versionCode, versionName))

    @staticmethod
    def _checkPath(path):
        if not os.path.exists(path):
            raise EnvironmentError('本地路径异常')


