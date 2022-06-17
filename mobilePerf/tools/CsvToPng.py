# -*- coding: <encoding name> -*- : # -*- coding: utf-8 -*-

import os
import csv
import csvToChart
import time

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
data_path = BASE_PATH + '/report'
re_data_path = data_path + '/prefData'
path = [data_path+'/CPU',data_path+'/FPS',data_path+'/MEM']
str = ["cpu","fps","mem"]

def check_file():
    if not os.path.exists(data_path):
        os.mkdir(data_path)
        path_list = ['/MEM', '/CPU', '/FPS']
        for i in path_list:
            if not os.path.exists(i):
                os.mkdir(data_path + i)

    elif os.path.exists(data_path):
        for i in path:
            file_or_dir = os.listdir(i)
            for file in file_or_dir:
                if file.startswith('CPU'):
                    data = path[0] + "/" + file
                    csvtopng(csvpath=data,cmd1=str[0])
                    print("cpu-png is done")

                elif file.startswith('FPS'):
                    data = path[1] + "/" + file
                    csvtopng(csvpath=data,cmd1=str[1])
                    print("fps-png is done")

                elif file.startswith('MEM'):
                    data = path[2] + "/" + file
                    csvtopng(csvpath=data,cmd1=str[2])
                    # print(data)
                    print("mem-png is done")
        return

def csvtopng(csvpath,cmd1):
        cmd = 'python3 /Users/cai.nianxi/Documents/nianxi/perfcode/mobilePerf/tools/csvToChart.py {} {}'.format(csvpath,cmd1)
        os.popen(cmd)
        return

if __name__ == '__main__':
    check_file()
