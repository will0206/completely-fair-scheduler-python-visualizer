import logging
import os
from datetime import datetime

dir_path = 'D:/碩士/OS_EDF-scheduling-master/MyCFS/logs/'   # 設定 logs 目錄
filename = "{:%Y-%m-%d}".format(datetime.now()) + '.log'     # 設定檔名

def create_logger(log_folder):
    # config
    logging.captureWarnings(True)   # 捕捉 py waring message
    formatter = logging.Formatter('%(message)s')
    my_logger = logging.getLogger('py.warnings')    # 捕捉 py waring message
    my_logger.setLevel(logging.DEBUG)

    # 若不存在目錄則新建
    if not os.path.exists(dir_path+log_folder):
        os.makedirs(dir_path+log_folder)

    # file handler
    fileHandler = logging.FileHandler(dir_path+log_folder+'/'+filename, 'w', 'utf-8')
    fileHandler.setFormatter(formatter)
    my_logger.addHandler(fileHandler)

    # console handler
    # consoleHandler = logging.StreamHandler()
    # consoleHandler.setLevel(logging.DEBUG)
    # consoleHandler.setFormatter(formatter)
    # my_logger.addHandler(consoleHandler)

    return my_logger