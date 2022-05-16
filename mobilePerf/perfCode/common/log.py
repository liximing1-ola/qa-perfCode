import os
import sys
import re
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
BaseDir=os.path.dirname(__file__)
sys.path.append(os.path.join(BaseDir, '../..'))
from mobilePerf.perfCode.common.utils import FileUtils
logger = logging.getLogger('mobileperf')
logger.setLevel(logging.DEBUG)
fmt = logging.Formatter('[%(asctime)s]%(levelname)s:%(name)s:%(module)s:%(message)s')
streamHandler=logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(fmt)
streamHandler.setLevel(logging.INFO)  # 调试时改为DEBUG 发布改为 INFO
dir = os.path.join(FileUtils.get_top_dir(), 'logs')
FileUtils.makedir(dir)
log_file = os.path.join(dir, "pref_log")
log_file_handler = TimedRotatingFileHandler(filename=log_file, when="D", interval=1, backupCount=3)
log_file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$")
log_file_handler.setFormatter(fmt)
log_file_handler.setLevel(logging.DEBUG)
logger.addHandler(streamHandler)
logger.addHandler(log_file_handler)

if __name__=="__main__":
	logger.debug("测试3！")