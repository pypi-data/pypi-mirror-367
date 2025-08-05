# -*- coding: UTF-8 -*-
import os

import q1x

# 执行成功
errno_success = 0
# qmt错误码基数
qmt_errno_base = 1000
# miniQMT 没有找到
errno_miniqmt_not_found = qmt_errno_base + 1
# quant1x.yaml配置文件没找到
errno_config_not_exist = qmt_errno_base + 2
# 连接miniQMT失败
errno_miniqmt_connect_failed = qmt_errno_base + 3
# 非交易日
errno_not_trade_day = qmt_errno_base + 4
# 缺少账户id
errno_not_found_account_id = qmt_errno_base + 5
# 缺少订单路径
errno_not_found_order_path = qmt_errno_base + 6

kFormatFileDate = '%Y%m%d'
kFormatOnlyDate = '%Y-%m-%d'
kFormatTimestamp = '%Y-%m-%d %H:%M:%S'
kTimestamp = '%H:%M:%S'
errBadSymbol = RuntimeError("无法识别的证券代码")


def get_quant1x_config_filename() -> str:
    """
    获取quant1x.yaml文件路径
    :return:
    """
    # 默认配置文件名
    default_config_filename = 'quant1x.yaml'
    yaml_filename = os.path.join('~', 'runtime', 'etc', default_config_filename)
    user_home = q1x.base.homedir()
    if not os.path.isfile(yaml_filename):
        quant1x_root = os.path.join(user_home, '.quant1x')
        yaml_filename = os.path.join(quant1x_root, default_config_filename)
        yaml_filename = os.path.expanduser(yaml_filename)
    yaml_filename = os.path.expanduser(yaml_filename)
    return yaml_filename
