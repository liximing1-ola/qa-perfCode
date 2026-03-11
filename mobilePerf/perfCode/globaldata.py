# -*- coding: utf-8 -*-
import threading


# 记录运行时需要共享的全局变量
class RuntimeData:
    old_pid = None
    packages = None
    package_save_path = None
    start_time = None
    exit_event = threading.Event()
    top_dir = None
    config_dic = {}
