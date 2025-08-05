# -*- coding: UTF-8 -*-
import os
import sys
import warnings
from dataclasses import dataclass, field

import q1x.base
import yaml
from q1x.base import TradingSession

from trader1x import utils
from trader1x.log4py import logger

warnings.filterwarnings('ignore')


def list_default_factory():
    return []


@dataclass
class TradeRule:
    """
    交易规则
    """
    id: int = -1  # 策略ID, -1无效
    auto: bool = False  # 是否自动执行
    name: str = None  # 策略名称
    flag: str = ''  # 订单标识,分早盘,尾盘和盘中
    time: TradingSession = field(default_factory=lambda: TradingSession("09:30:00~11:30:00,13:00:00~14:56:30"))
    weight: int = 0  # 策略权重, 默认0, 由系统自动分配
    total: int = 3  # 订单总数, 默认是3
    fee_max: float = 20000.00  # 可投入资金-最大
    fee_min: float = 10000.00  # 可投入资金-最小
    sectors: list[str] = None  # 板块, 策略适用的板块列表, 默认板块为空, 即全部个股
    ignore_margin_trading: bool = True  # 剔除两融标的, 默认是剔除

    def __init__(self, params: dict = None):
        """
        初始化
        """
        # 先让 dataclass 初始化默认值
        # 手动初始化所有字段
        self.time = TradingSession("09:30:00~11:30:00,13:00:00~14:56:30")
        if params is None:
            return
        for key, value in params.items():
            if not hasattr(self, key):
                continue
            tmp_value = getattr(self, key)
            if isinstance(tmp_value, TradingSession):
                new_value = TradingSession(value)
                setattr(self, key, new_value)
            else:
                setattr(self, key, value)

    def enable(self) -> bool:
        """
        是否有效
        :return:
        """
        return self.auto and self.id >= 0

    def buy_enable(self) -> bool:
        """
        买入有效
        :return:
        """
        return self.enable() and self.total > 0

    def sell_enable(self) -> bool:
        """
        卖出有效
        :return:
        """
        return self.enable()

    def is_cookie_cutter_for_sell(self) -> bool:
        """
        是否一刀切卖出
        :return:
        """
        return self.sell_enable() and self.total == 0


@dataclass
class TraderConfig:
    """
    配置信息
    """
    # 账号ID
    account_id: str = ''
    # 运行路径
    order_path: str = ''
    # 时间范围 - 早盘策略
    head_time: TradingSession = field(default_factory=lambda: TradingSession("09:27:00~14:57:00"))
    # 时间范围 - 尾盘策略
    tail_time: TradingSession = field(default_factory=lambda: TradingSession("14:45:00~14:59:50"))
    # 时间范围 - 盘中订单
    tick_time: TradingSession = field(default_factory=lambda: TradingSession("09:39:00-14:57:00"))
    # 时间范围 - 持仓卖出
    ask_time: TradingSession = field(default_factory=lambda: TradingSession("09:50:00~14:59:30"))
    # 时间范围 - 撤销订单
    cancel_time: TradingSession = field(default_factory=lambda: TradingSession("09:15:00~09:19:59, 09:30:00~14:56:59"))
    # 时间范围 - 盘后复盘
    review_time: TradingSession = field(default_factory=lambda: TradingSession("00:00:00~08:30:00, 15:01:00~23:59:59"))
    # 买入持仓率, 资金控制阀值
    position_ratio: float = 0.5000
    # 印花税 - 买入, 按照成交金额, 买入0.0%
    stamp_duty_rate_for_buy: float = 0.0000
    # 印花税 - 卖出, 按照成交金额, 卖出0.1%
    stamp_duty_rate_for_sell: float = 0.0010
    # 过户费 - 双向, 按照数量收取, 默认万分之六, 0.06%
    transfer_rate: float = 0.0006
    # 券商佣金 - 双向, 按成交金额计算, 默认万分之二点五, 0.025%
    commission_rate: float = 0.00025
    # 券商佣金最低, 默认5.00
    commission_min: float = 5.00
    # 保留现金
    keep_cash: float = 10000.00
    # tick订单最大金额, 默认20000.00
    tick_order_max_amount: float = 20000.00
    # tick订单最小金额, 默认10000.00
    tick_order_min_amount: float = 10000.00
    # 买入最大金额
    buy_amount_max: float = 250000.00
    # 买入最小金额
    buy_amount_min: float = 1000.00
    # 每策略最多可买股票数量, 这里默认3
    max_stock_quantity_for_strategy: int = 3
    # 自动卖出, 默认为True
    sell_order_auto: bool = False
    # 自动交易head订单, 默认为True
    head_order_auto: bool = False
    # 自动交易tick订单, 默认为True
    tick_order_auto: bool = False
    # 自动交易tail订单, 默认为True
    tail_order_auto: bool = False

    # 启动了mimiQMT机器的代理服务的监听地址, 默认为回环地址127.0.0.1, 强烈不推荐使用0.0.0.0
    proxy_address: str = q1x.base.lan_address()
    # 代理服务的监听端口, 默认18168
    proxy_port: int = 18168
    # 代理服务默认工作线程数, 默认为cpu核数的二分之一
    proxy_workers: int = q1x.base.max_procs()
    # qmt proxy地址
    proxy_url: str = ""
    # 策略集合
    strategies: list[TradeRule] = list_default_factory
    # 可撤单的交易时段
    cancel: TradingSession = field(
        default_factory=lambda: TradingSession("09:15:00~09:19:59,09:25:00~11:29:59,13:00:00~14:59:59"))

    def __fix_instance(self):
        """
        加载后修复
        :return:
        """
        if isinstance(self.ask_time, str):
            ts = TradingSession(self.ask_time)
            if ts.is_valid():
                self.ask_time = ts
        if isinstance(self.cancel_time, str):
            ts = TradingSession(self.cancel_time)
            if ts.is_valid():
                self.cancel_time = ts
        if isinstance(self.tick_time, str):
            ts = TradingSession(self.tick_time)
            if ts.is_valid():
                self.tick_time = ts

    def __post_init__(self):
        """
        __init__()后调用, 调整类型
        :return:
        """
        self.__fix_instance()


# 全局变量 - 配置
__global_config = TraderConfig()


def load(config_filename: str = '') -> TraderConfig:
    """
    加载配置文件
    :return:
    """
    global __global_config
    config = TraderConfig()
    config_filename = config_filename.strip()
    if len(config_filename) == 0:
        config_filename = utils.get_quant1x_config_filename()
    config_filename = os.path.expanduser(config_filename)
    logger.info(config_filename)
    if not os.path.isfile(config_filename):
        logger.error('QMT config {}: 不存在', config_filename)
        sys.exit(utils.errno_config_not_exist)
    try:
        with open(config_filename, 'r', encoding='utf-8') as f:
            result = yaml.load(f, Loader=yaml.FullLoader)
            key_trader = "trader"
            if isinstance(result, dict) and key_trader in result:
                trader = result[key_trader]
                for key, value in trader.items():
                    if not hasattr(config, key):
                        continue
                    tmp_value = getattr(config, key)
                    if isinstance(tmp_value, TradingSession):
                        new_value = TradingSession(value)
                        setattr(config, key, new_value)
                    elif tmp_value is list_default_factory:
                        if key == 'strategies':
                            tmp_list = []
                            if isinstance(value, list):
                                for d in value:
                                    rule = TradeRule(d)
                                    tmp_list.append(rule)
                            setattr(config, key, tmp_list)
                    elif key == 'account_id':
                        setattr(config, 'account_id', str(value))
                    elif key == 'top_n':
                        setattr(config, 'max_stock_quantity_for_strategy', value)
                    else:
                        setattr(config, key, value)
    except Exception as e:
        logger.error(f"发生了一个错误：{config_filename}\n错误信息：{e}")
        logger.warning('系统将使用默认配置')
        config = TraderConfig()
    # finally:
    #     logger.warning('系统将使用默认配置')
    # 检查重点配置
    if config.account_id == '':
        logger.error('配置缺少账户id')
        sys.exit(utils.errno_not_found_account_id)
    if config.order_path == '':
        logger.error('配置缺少订单路径')
        sys.exit(utils.errno_not_found_order_path)
    __global_config = config
    return config


def get() -> TraderConfig:
    global __global_config
    return __global_config


if __name__ == '__main__':
    filename = '~/.q2x/quant1x.yaml'
    config = load(filename)
    print(config)
