import sys
import os
import time
from nt import chdir

now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
if len(sys.argv) != 5:
    print('-----------INPUT[apkPath][apkName][appVersion][CPU]-----------')
    quit(0)
apk_file_name = sys.argv[1]
app_name = sys.argv[2]
app_version = sys.argv[3]
app_so = sys.argv[4]
output_path = 'D:/Build/{}_{}_{}_{}'.format(app_name, app_version, app_so, now)


# 出主渠道包
def process_one_conf(channel_list):
    # 本地路径
    if os.path.exists(output_path):
        print('existed')
    else:
        os.makedirs(output_path)
    for channel_name in channel_list:
        cmd = 'java -jar walle-cli-all.jar batch -c ' + channel_name + ' ' + apk_file_name + ' ' + output_path
        os.system(cmd)
    change_name(output_path)
    app_list = os.listdir(output_path)
    print(app_list)
    print('--------------BuildSuccess，ApkPath==[ {} ]--------------'.format(output_path))


def change_name(path):
    os.chdir(path)
    app_list = os.listdir(path)
    for app in app_list:
        if app.endswith('.apk'):
            apk_name = app[:-4]
            apk_name_1 = apk_name.split('-')
            channel_name = apk_name_1[-1].split('_')[1]
            app_name_2 = apk_name_1[0] + '-' + channel_name + '-release' + '-{}'.format(app_so)
            os.rename(apk_name + '.apk', app_name_2 + '.apk')
        else:
            print('Not OK')


def appBuild():
    if app_name.startswith('slp'):
        channel = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'baidu']
        process_one_conf(channel)
    elif app_name.startswith('rbp'):
        channel = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb']
        process_one_conf(channel)
    else:
        channel_names = ['gw', 'oppo', 'vivo', 'huawei', 'xiaomi', 'yyb', 'rongyao']
        process_one_conf(channel_names)


if __name__ == '__main__':
    appBuild()