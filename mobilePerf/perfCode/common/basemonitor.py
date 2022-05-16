# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger(__name__)
class Monitor(object):

    def __init__(self, **kwargs):
        """构造器
        :param dict kwargs: 配置项
        """
        self.config = kwargs  # 配置项
        self.matched_data = {}  # 采集到匹配的性能数据

    def start(self):
        """子类中实现该接口，开始采集性能数据"""
        logger.warning("请在%s类中实现start方法" % type(self))

    def clear(self):
        """清空monitor保存的数据"""
        self.matched_data = {}

    def stop(self):
        """子类中实现该接口，结束采集性能数据，如果后期需要解析性能数据，需要保存数据文件"""
        logger.warning("请在%s类中实现stop方法" % type(self))

    def save(self):
        """保存数据
        """
        logger.warning("请在%s类中实现save方法" % type(self))


if __name__ == '__main__':
    pass