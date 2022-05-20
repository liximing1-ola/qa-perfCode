import csv
import os  # for in mac
import platform
from matplotlib.pylab import *

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = BASE_PATH + '/report'


def csvToChart(platforms):
    csv_path = ''
    y_name = ' '
    perf = ''
    if platforms == 'win':
        print('platform=Windows\n')
        if len(sys.argv) == 3:
            csv_path = sys.argv[1]
            perf = sys.argv[2].upper()  # perf = re.split('\\\\', csv_path)[4]
        else:
            perf = sys.argv[1].upper()
            for i, j, csv_path in os.walk(data_path + '/{}'.format(perf)):
                if len(csv_path) == 0:
                    print('未生成有效数据')
                    exit(1)
            csv_path = data_path + '/{}/{}'.format(perf, csv_path[-1])  # 默认时间倒序最后一个csv文件，根据需要修改
    elif platforms == 'mac':
        print('platform=Mac\n')
        if len(sys.argv) != 2:
            print('mac need input one key, eg（cpu, mem, fps）')
            exit(1)
        perf = sys.argv[1].upper()
        for i, j, csv_path in os.walk(data_path + '/{}'.format(perf)):
            if len(csv_path) == 0:
                print('未生成有效数据')
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

    title_show = 'BANBAN_{}_Analysis'.format(perf)  # 根据APP调整展示title
    if perf == 'FPS':
        y_name = 'FPS(gfxinfo)'
    elif perf == 'CPU':
        y_name = 'CPU(%)'
    elif perf == 'MEM':
        y_name = 'MEM(m)'
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
                        float(data_list[1])) <= 60:  # 根据设备gfxinfo信息计算1s内超时帧时间，反推出实际帧率，根据实际设备修改阈值
                    y.append(round(float(data_list[1])))
            del y[1::2]  # 隔一个取一个值，影响不大
            return y
    elif perf == 'CPU':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(float(data_list[1])) <= 100:  # 顶层activity所在进程的CPU占用百分比
                    y.append(round(float(data_list[1])))
            del y[1::2]
            return y
    elif perf == 'MEM':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:  # 顶层activity所在进程的PSS（实际使用内存）
                if round(float(data_list[1])) != 0:
                    y.append(round(float(data_list[1])))
            del y[1::2]
            return y
    else:
        print('input error')


if __name__ == '__main__':
    if platform.system() == 'Windows':
        csvToChart('win')
    elif platform.system() == 'Darwin':
        csvToChart('mac')
