import csv
import platform
from matplotlib.pylab import *
import os
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = BASE_PATH + '/report'


def csvToChart(platforms):
    csv_path = ''
    y_name = ' '
    perf = ''
    if platforms == 'win':  # windows设备
        print('platform=Windows\n')
        if len(sys.argv) == 3:
            csv_path = sys.argv[1]
            perf = sys.argv[2].upper()  # perf = re.split('\\\\', csv_path)[4]
        else:
            perf = sys.argv[1].upper()
            for i, j, csv_path in os.walk(data_path + '/{}'.format(perf)):
                if len(csv_path) == 0:
                    print('invalid data')
                    exit(1)
            csv_path = data_path + '/{}/{}'.format(perf, csv_path[-1])  # 默认时间倒序最后一个csv文件，根据需要修改
    elif platforms == 'mac':  # iOS设备
        print('platform=Mac\n')
        if len(sys.argv) != 2:
            print('mac need input one key, eg（cpu, mem, fps）')
            exit(1)
        perf = sys.argv[1].upper()
        for i, j, csv_path in os.walk(data_path + '/{}'.format(perf)):
            if len(csv_path) == 0:
                print('')
                exit(1)
            csv_path = data_path + '/{}/{}'.format(perf, csv_path[-1])  # 默认时间倒序最后一个csv文件，根据需要修改

    if not csv_path:
        return
    print(csv_path, perf)

    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    plt.rcParams['figure.figsize'] = [8.0, 4.0]  # 设置图片格式像素等
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    plt.rcParams['savefig.dpi'] = 200
    plt.rcParams['figure.dpi'] = 100

    title_show = 'APP_{}_Analysis'.format(perf)  # 根据APP调整展示title
    if perf == 'FPS':
        y_name = 'FPS(gfxinfo)'
    elif perf == 'CPU':
        y_name = 'CPU(%)'
    elif perf == 'MEM':
        y_name = 'MEM(m)'
    elif perf == 'TEMP':
        y_name = 'Temp(℃)'
    y = csvToList(csv_path, perf)
    x = range(1, len(y) + 1)
    try:
        if y and len(x) == len(y):
            plt.plot(x, y)
            plt.xlabel('Time Consuming', color='r')
            plt.ylabel('{}'.format(y_name), color='r', size=16)
            plt.title(title_show, color='g', size=18)
            plt.grid(True)
            plt.savefig(data_path + '/{}/{}.png'.format(perf, now))
            plt.show()
    except Exception as error:
        print(error)


def csvToList(csv_path, perf):
    y = []
    if perf == 'FPS':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(
                        float(data_list[1])) <= 90:
                    # 根据gfxinfo信息计算1s内超时帧时间，计算出实际帧率（根据设备情况修改阈值，flutter=60）
                    y.append(round(float(data_list[1])))
            del y[1::2]
            return y
    elif perf == 'CPU':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(float(data_list[1])) <= 100:  # 顶层activity所在进程的CPU占用百分比
                    y.append(round(float(data_list[1])))
            y.remove(max(y))
            y.remove(min(y))
            print('max：{}'.format(min(y)))
            print('min：{}'.format(max(y)))
            print('av：{}'.format(int(sum(y) / len(y))))
            del y[1::2]
            return y
    elif perf == 'MEM':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:  # 顶层activity所在进程的PSS（实际使用内存）
                if round(float(data_list[1])) != 0:
                    y.append(round(float(data_list[1])))
            print('min：{}'.format(min(y)))
            print('max：{}'.format(max(y)))
            print('av：{}'.format(int(sum(y)/len(y))))
            del y[1::2]
            return y
    elif perf == 'TEMP':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0:
                    y.append(round(float(data_list[1])))
            print('min：{}'.format(min(y)))
            print('max：{}'.format(max(y)))
            print('av：{}'.format(int(sum(y)/len(y))))
            del y[1::2]
            return y
    else:
        print('input error')


if __name__ == '__main__':
    if platform.system() == 'Windows':  # win设备
        csvToChart('win')
    elif platform.system() == 'Darwin':  # ios 设备
        csvToChart('mac')