import csv
from pylab import *
def csvToChart():
    if len(sys.argv) != 2:
        print('input path')
        exit(1)

    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    csv_path = sys.argv[1]
    perf = re.split('\\\\', csv_path)[4]
    y = csvToList(csv_path, perf)
    x = range(1, len(y)+1)

    if perf == 'FPS':
        title_show = 'BANBAN_FPS'
        try:
            if y and len(x) == len(y):
                plt.plot(x, y)
                plt.xlabel('Time(s)', color='r')
                plt.ylabel('FPS', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig('E:/report/FPS/{}.png'.format(now))
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
                plt.xlabel('Time(s)', color='r')
                plt.ylabel('CPU(%)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig('E:/report/CPU/{}.png'.format(now))
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
                plt.xlabel('Time(s)', color='r')
                plt.ylabel('MEM(M)', color='r')
                plt.title(title_show, color='g')
                plt.grid(True)
                plt.savefig('E:/report/MEM/{}.png'.format(now))
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
            return y

    elif perf == 'CPU':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0 and round(float(data_list[1])) <= 120:
                    y.append(round(float(data_list[1])))
                else:
                    pass
            return y

    elif perf == 'MEM':
        with open(csv_path, 'r+', encoding='gbk') as file:
            for data_list in [i for i in csv.reader(file)][1:]:
                if round(float(data_list[1])) != 0:
                    y.append(round(float(data_list[1])))
                else:
                    pass
            return y

    else:
        print('输入异常')


if __name__=='__main__':
    csvToChart()