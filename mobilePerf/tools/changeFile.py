import os
import time
import shutil
import subprocess

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = BASE_PATH + '/report'
re_data_path = data_path + '/prefData'


def check_file():
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        path_list = ['/MEM', '/CPU', '/FPS']
        for i in path_list:
            if not os.path.exists(i):
                os.mkdir(data_path + i)


def lsPhoneFile():
    command = 'adb shell ls /storage/emulated/0/solopi/'  # solopi 地址路径
    solopi_path = 'records/records'  # 自己通过solopi的路径设置
    file_list = []
    if not is_exist(command):
        exit(1)
    res = subprocess.Popen(command + solopi_path,
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    stdout, stderr = res.communicate()
    if res.returncode == 0:
        print('性能采集点文件夹(时间正序排列)：\n{}'.format(stdout))
        file_list.append(res.communicate()[0])
        return file_list[0].split('\n')
    elif stdout == '' and res.poll() is not None:
        exit(1)
    else:
        print('请检查设备USB链接 or 确保数据输出到指定文件夹\n')
        exit(1)


def is_exist(path):
    """
    判断文件或文件夹是否存在
    :param path:
    :return:
    """
    result = subprocess.Popen(path, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)
    if not result:
        return False
    result = result.stderr.readline().decode('utf-8')
    if 'No such file or directory' in result:
        print('please install solopi apk\n')
        return False
    return True


def changeFile():
    try:
        now_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        print('当前执行时间: {} \n'.format(now_time))
        # perf_data_path = str(input('请选择复制要获取的性能采集文件夹(1=退出)：{}'.format(lsPhoneFile()[-2])))
        file_name= lsPhoneFile()[-2]
        print('默认获取的性能采集文件夹: {}\n'.format(file_name))
        perf_data_path = file_name
        if int(perf_data_path) == 1:
            print('\n退出成功')
            exit(1)
        check_file()
        if os.path.exists(re_data_path):
            shutil.rmtree(re_data_path)
        cmd = 'adb pull /storage/emulated/0/solopi/records/records/{} {}'.format(perf_data_path, data_path)
        os.popen(cmd)
        time.sleep(1)
        os.rename('{}/{}'.format(data_path, perf_data_path), '{}'.format(re_data_path))
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        file_or_dir = os.listdir(re_data_path)
        for file_dir in file_or_dir:
            if file_dir.startswith('帧率_FPS'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/FPS' + '/FPS_{}.csv'.format(now))
                print('fps 执行成功')

            elif file_dir.startswith('PSS-main'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/MEM' + '/MEM_{}.csv'.format(now))
                print('mem 执行成功')

            elif file_dir.startswith('应用进程-main'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/CPU' + '/CPU_{}.csv'.format(now))
                print('cpu 执行成功')
            else:
                pass

        print('执行成功，请查看本地路径 {}'.format(data_path))
    except EOFError as error:
        print('输入异常', error)
        exit(1)
    except Exception as error:
        print(error)
        exit(1)


if __name__ == '__main__':
    changeFile()
