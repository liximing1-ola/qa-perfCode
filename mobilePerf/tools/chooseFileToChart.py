import os
import time
import shutil
import subprocess

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = os.path.join(BASE_PATH, 'report')
re_data_path = os.path.join(data_path, 'prefData')
solopi_path = 'records/records/records'  # 自己通过solopi的路径设置
path_list = ['MEM', 'CPU', 'FPS', 'TEMP']


def lsPhoneFile():
    command = 'adb shell ls /storage/emulated/0/solopi/records/'  # solopi 地址路径
    file_list = []
    use_file = []
    if not is_exist(command+solopi_path):
        print('请检查设备USB连接 or 确保数据输出到指定文件夹\n')
        exit(1)
    res = subprocess.Popen(command + solopi_path,
                           shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    stdout, stderr = res.communicate()
    if res.returncode == 0:
        print('数据采集点文件夹(按照时间正序排列)：\n{}'.format(stdout))
        file_list.append(res.communicate()[0])
        file_list = file_list[0].split('\n')
        for i in file_list:
            if len(i) == 29:  # 正常生成文件夹长度
                use_file.append(i)
        return use_file[-1]
    elif stdout == '' and res.poll() is not None:
        exit(1)
    else:
        pass


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
        print('Please Install APK\n')
        return False
    return True


def main():
    try:
        now_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        print('当前执行时间: {} \n'.format(now_time))
        lsPhoneFile()
        perf_data_path = str(input('选择复制要获取的性能数据文件夹(1=退出): '))
        if perf_data_path == '1':
            exit(1)
        if not os.path.exists(data_path):
            os.mkdir(data_path)
            for i in path_list:
                if not os.path.exists(data_path + i):
                    os.mkdir(data_path + i)
        if os.path.exists(re_data_path):
            shutil.rmtree(re_data_path)
        cmd = 'adb pull /storage/emulated/0/solopi/records/{}/{} {}'.format(solopi_path, perf_data_path, data_path)
        os.popen(cmd)
        time.sleep(1)
        os.rename('{}/{}'.format(data_path, perf_data_path), '{}'.format(re_data_path))
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        file_or_dir = os.listdir(re_data_path)
        for file_dir in file_or_dir:
            if file_dir.startswith('帧率_FPS'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/FPS' + '/FPS_{}.csv'.format(now))
                print('FPS success')

            elif file_dir.startswith('PSS_main'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/MEM' + '/MEM_{}.csv'.format(now))
                print('MEM success')

            elif file_dir.startswith('process_main'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/CPU' + '/CPU_{}.csv'.format(now))
                print('CPU success')

            elif file_dir.startswith('CPU温度_Temperature'):
                shutil.move(os.path.join(re_data_path, file_dir), data_path + '/TEMP' + '/TEMP_{}.csv'.format(now))
                print('TEMP success')
            else:
                pass

        print('执行成功，请查看当前路径下文件 {}'.format(data_path))
    except EOFError as error:
        print('请检查你的输入项', error)
        exit(1)
    except Exception as error:
        print(error)
        exit(1)


if __name__ == '__main__':
    main()
import os
import time
import shutil
import subprocess
from typing import List, Optional

# Constants - grouped at the top for easier maintenance
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DATA_PATH = os.path.join(BASE_PATH, 'report')
RE_DATA_PATH = os.path.join(DATA_PATH, 'prefData')
SOLOPI_PATH = 'records/records/records'  # Solopi path setting
PATH_LIST = ['MEM', 'CPU', 'FPS', 'TEMP']
ADB_BASE_COMMAND = 'adb shell ls /storage/emulated/0/solopi/records/'


def run_adb_command(command: str) -> tuple[Optional[str], Optional[str]]:
    """Execute ADB command and return (stdout, stderr)"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8',
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        print(f"ADB command timed out: {command}")
        return None, "Timeout error"
    except Exception as e:
        print(f"Error executing ADB command: {str(e)}")
        return None, str(e)


def is_adb_device_connected() -> bool:
    """Check if ADB device is connected"""
    stdout, _ = run_adb_command('adb devices')
    return 'device' in stdout if stdout else False


def list_solopi_directories() -> Optional[List[str]]:
    """List available Solopi data directories on device"""
    if not is_adb_device_connected():
        print("No ADB device connected. Please check USB connection.")
        return None

    command = f'{ADB_BASE_COMMAND}{SOLOPI_PATH}'
    stdout, stderr = run_adb_command(command)

    if not stdout:
        print(f"Failed to list directories: {stderr}")
        return None

    # Filter valid directories (29-character timestamps)
    return [dir for dir in stdout.split('\n') if len(dir.strip()) == 29]


def create_data_directories() -> None:
    """Create necessary data directories if they don't exist"""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created main data directory: {DATA_PATH}")

    for dir_name in PATH_LIST:
        dir_path = os.path.join(DATA_PATH, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created subdirectory: {dir_path}")


def pull_and_organize_data(perf_data_path: str) -> bool:
    """Pull data from device and organize into appropriate directories"""
    try:
        # Clean up previous data
        if os.path.exists(RE_DATA_PATH):
            shutil.rmtree(RE_DATA_PATH)
            print(f"Removed existing data directory: {RE_DATA_PATH}")

        # Pull data from device
        pull_cmd = (f'adb pull /storage/emulated/0/solopi/records/{SOLOPI_PATH}/'
                   f'{perf_data_path} {DATA_PATH}')
        print(f"Pulling data with command: {pull_cmd}")

        stdout, stderr = run_adb_command(pull_cmd)
        if stderr:
            print(f"Error pulling data: {stderr}")
            return False

        # Rename pulled directory
        source_path = os.path.join(DATA_PATH, perf_data_path)
        os.rename(source_path, RE_DATA_PATH)
        print(f"Data pulled to: {RE_DATA_PATH}")

        # Organize files by type
        now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        file_types = {
            '帧率_FPS': ('FPS', 'FPS'),
            'PSS_main': ('MEM', 'MEM'),
            'process_main': ('CPU', 'CPU'),
            'CPU温度_Temperature': ('TEMP', 'TEMP')
        }

        for file_dir in os.listdir(RE_DATA_PATH):
            source_file = os.path.join(RE_DATA_PATH, file_dir)
            for prefix, (dest_dir, prefix_name) in file_types.items():
                if file_dir.startswith(prefix):
                    dest_path = os.path.join(DATA_PATH, dest_dir, f'{prefix_name}_{now}.csv')
                    shutil.move(source_file, dest_path)
                    print(f"Moved {prefix} data to: {dest_path}")
                    break
            else:
                print(f"Ignoring unknown file: {file_dir}")

        return True

    except Exception as e:
        print(f"Error organizing data: {str(e)}")
        return False


def main():
    try:
        now_time = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        print(f'当前执行时间: {now_time}\n')

        # Get available directories
        dirs = list_solopi_directories()
        if not dirs:
            print("No valid data directories found on device")
            return

        print('数据采集点文件夹(按照时间正序排列):')
        for i, dir_name in enumerate(dirs, 1):
            print(f"{i}. {dir_name}")

        # Get user input
        while True:
            perf_data_input = input('选择复制要获取的性能数据文件夹(输入序号或1=退出): ')
            if perf_data_input == '1':
                print("Exiting program")
                return

            if perf_data_input.isdigit():
                index = int(perf_data_input) - 1
                if 0 <= index < len(dirs):
                    perf_data_path = dirs[index]
                    break

            print("Invalid input. Please enter a valid number.")

        # Create directories and organize data
        create_data_directories()
        if pull_and_organize_data(perf_data_path):
            print(f'执行成功，请查看当前路径下文件: {DATA_PATH}')
        else:
            print("数据处理失败")

    except EOFError:
        print('输入错误，请检查输入项')
    except Exception as error:
        print(f"发生错误: {str(error)}")


if __name__ == '__main__':
    main()
