import os
import re
import sys


#  检查apk版本号等信息
def getAppBaseInfo():
    aapt_path = 'D:/build-tools/33.0.0/aapt.exe'  # aapt.exe路径
    apk_path = sys.argv[1]
    get_info_command = "{} dump badging {}".format(aapt_path, apk_path)
    output = os.popen(get_info_command)  # 执行命令，并将结果以字符串方式返回
    output = output.buffer.read().decode(encoding='utf-8')
    match = re.compile("package: name='(\S+)' versionCode='(\d+)' versionName='(\S+)'").match(
        output)  # 通过正则匹配，获取包名，版本号，版本名称
    if not match:
        print(output)
        raise Exception("can't get packageInfo")
    packageName = match.group(1)
    versionCode = match.group(2)
    versionName = match.group(3)
    print(" 包名：%s \n 版本号：%s \n 版本名称：%s " % (packageName, versionCode, versionName))


if __name__ == '__main__':
    getAppBaseInfo()
