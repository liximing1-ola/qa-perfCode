import csv
import os  # for in mac
import platform
from matplotlib.pylab import *
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = BASE_PATH + '/report'
def csvToChart_win():
    csv_path = ''
    if len(sys.argv) == 3:
        csv_path = sys.argv[1]
        perf = sys.argv[2].upper()
        # perf = re.split('\\\\', csv_path)[4]
        print(perf, csv_path)
    else:
        perf = sys.argv[1].upper()
        for i, j, k in os.walk(data_path + '/{}'.format(perf)):
            if len(k) == 0:
                print('未生成有效数据')
                exit(1)
            csv_path = data_path + '/{}/{}'.format(perf, k[-1])  # 默认时间倒序最后一个csv文件，根据需要修改
        print(perf, csv_path)

    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    y = csvToList(csv_path, perf)
    x = range(1, len(y) + 1)
    #  设置图片格式像素等
    plt.rcParams['figure.figsize'] = [8.0, 4.0]
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    plt.rcParams['savefig.dpi'] = 200
    plt.rcParams['figure.dpi'] = 100

    if perf == 'FPS':
        title_show = 'BANBAN_FPS'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('FPS', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/FPS/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)

    elif perf == 'CPU':
        title_show = 'BANBAN_CPU'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('CPU(%)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/CPU/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)

    elif perf == 'MEM':
        title_show = 'BANBAN_MEM'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('MEM(M)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/MEM/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)

def csvToChart_mac():
    if len(sys.argv) != 2:
        print('mac need input one key, eg（cpu, mem, fps）')
        exit(1)
    perf = sys.argv[1].upper()
    csv_path = ''
    for i, j, k in os.walk(data_path + '/{}'.format(perf)):
        if len(k) == 0:
            print('未生成有效数据')
            exit(1)
        csv_path = data_path + '/{}/{}'.format(perf, k[-1])  # 默认时间倒序最后一个csv文件，根据需要修改
        print(perf, csv_path)
    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    y = csvToList(csv_path, perf)
    x = range(1, len(y) + 1)

    #  设置图片格式像素等
    plt.rcParams['figure.figsize'] = [8.0, 4.0]
    plt.rcParams['image.interpolation'] = 'nearest'
    plt.rcParams['image.cmap'] = 'gray'
    plt.rcParams['savefig.dpi'] = 200
    plt.rcParams['figure.dpi'] = 100

    if perf == 'FPS':
        title_show = 'BANBAN_FPS'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('FPS', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/FPS/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)

    elif perf == 'CPU':
        title_show = 'BANBAN_CPU'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('CPU(%)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/CPU/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)

    elif perf == 'MEM':
        title_show = 'BANBAN_MEM'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time', color='r')
                plt.ylabel('MEM(M)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig(data_path + '/MEM/{}.png'.format(now))
                plt.show()
            else:
                print(' x != y')
        except Exception as error:
            print(error)


def csvToList(csv_path, perf):
    y = []
    if perf == 'FPS':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(float(data_list[1])) <= 60:  # 过滤垃圾数据
                    y.append(round(float(data_list[1])))
                else:
                    pass
            del y[1::2]  # 隔一个取一个
            return y

    elif perf == 'CPU':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(float(data_list[1])) <= 120:
                    y.append(round(float(data_list[1])))
                else:
                    pass
            del y[1::2]
            return y

    elif perf == 'MEM':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0:
                    y.append(round(float(data_list[1])))
                else:
                    pass
            del y[1::2]
            return y

    else:
        print('输入异常')


if __name__ == '__main__':
    if platform.system() == 'Windows':
        csvToChart_win()
    elif platform.system() == 'Darwin':
        csvToChart_mac()