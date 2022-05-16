import random
import time
class config:
    package = 'com.imbb.banban.android'
    deviceId = 'b286dc11'
    period = 30  # 时间间隔默认30s
    # 网络
    net = "wifi"
    # 指定伪随机数生成器的seed值
    monkey_seed = str(random.randrange(1, 1000))
    # monkey 参数
    monkey_parameters = "--throttle 500 --ignore-crashes --ignore-timeouts --pct-touch 50 –-pct-nav 20 " \
                         "--pct-appswitch 15 --pct-syskeys 5 --pct-motion 5 –-pct-majornav 5 -v -v 10000"

    # log保存地址(时间格式为日-时-分)
    now = time.strftime('%d-%H-%M', time.localtime(time.time()))
    log_location = "E:/report/log/" + str(now) + "-log.txt"
    # 性能数据存储目录
    info_path = "E:/report"
