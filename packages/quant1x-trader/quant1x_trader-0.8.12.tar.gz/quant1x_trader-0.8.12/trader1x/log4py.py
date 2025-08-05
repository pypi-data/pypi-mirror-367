# -*- coding: UTF-8 -*-
import os
import sys

import yaml
from loguru import logger as __logger
from q1x.base import file, application

from trader1x import utils

# 获取默认的配置文件路径
config_filename = utils.get_quant1x_config_filename()
# 转换用户路径
config_filename = os.path.expanduser(config_filename)
# 检查配置文件是否存在
if not os.path.isfile(config_filename):
    __logger.error('QMT config {}: 不存在', config_filename)
    sys.exit(utils.errno_config_not_exist)

try:
    with open(config_filename, 'r', encoding='utf-8') as f:
        result = yaml.load(f, Loader=yaml.FullLoader)
        key_basedir = "basedir"
        if isinstance(result, dict) and key_basedir in result:
            quant1x_data_path = result[key_basedir]
except Exception as e:
    quant1x_data_path = file.homedir()
quant1x_data_path = os.path.expanduser(quant1x_data_path)
_, filename, _ = application()
if filename == 'pythonservice':
    filename = 'proxy'
__log_file = f"{quant1x_data_path}/logs/{filename}.log"
# print(__log_file)
__logger.add(__log_file, encoding="utf-8", rotation="00:00", retention="10 days")

logger = __logger
