# coding=utf-8
import os
import time

import pandas as pd
from xtquant import xtdata
from xtquant.xttype import StockAccount

from trader1x import utils
from trader1x.config import TraderConfig
from trader1x.log4py import logger

# 禁止显示XtQuant的hello信息
xtdata.enable_hello = False

order_buy = 1
order_sell = 2
order_junk = 3
flag_buy = "b"
flag_sell = "s"
flag_junk = "j"


class QmtContext(object):
    """
    QMT 上下文
    TODO: 按日期切换数据
    """
    current_date: str  # 当前日期
    config_filename: str  # 配置文件名
    order_path: str  # quant1x系统输出订单的路径
    account_id: str  # 账号ID
    t89k_order_file: str  # 订单文件
    t89k_flag_ready: str  # 订单就绪标志
    t89k_flag_done: str  # 订单执行完成标志
    positions_sell_done: str  # 持仓卖出状态
    qmt_order_filename: str  # qmt系统输出的订单路径
    qmt_order_done: str  # qmt系统每日订单刷新完成标志
    qmt_positions_filename: str # qmt持仓

    def __init__(self, conf: TraderConfig):
        self._config = conf
        self.current_date = time.strftime(utils.kFormatFileDate)
        self.account_id = conf.account_id
        self.order_path = conf.order_path
        self.switch_date()

    def account(self) -> StockAccount:
        return StockAccount(self.account_id)

    def sell_is_ready(self) -> bool:
        """
        卖出条件是否就绪
        :return:
        """
        return self._config.ask_time.is_trading()

    def sell_is_auto(self) -> bool:
        """
        卖出操作是否自动一刀切
        :return:
        """
        return self._config.sell_order_auto

    def head_order_is_ready(self) -> bool:
        """
        早盘(买入)订单是否准备就绪
        :return:
        """
        if os.path.isfile(self.t89k_flag_ready) and os.path.isfile(self.t89k_order_file):
            return True
        return False

    def head_order_is_auto(self) -> bool:
        """
        是否执行 早盘订单的交易
        :return:
        """
        return self._config.head_order_auto

    def tick_order_is_auto(self) -> bool:
        """
        是否执行 盘中即时订单的交易
        :return:
        """
        return self._config.tick_order_auto

    def tail_order_is_auto(self) -> bool:
        """
        是否执行 尾盘订单的交易
        :return:
        """
        return self._config.tail_order_auto

    def can_review(self) -> bool:
        """
        是佛可以复盘
        :return:
        """
        return self._config.review_time.is_trading()

    def load_head_order(self) -> pd.DataFrame:
        """
        加载早盘订单
        :return:
        """
        df = pd.read_csv(self.t89k_order_file)
        return df

    def switch_date(self):
        """
        重置属性
        :return:
        """
        logger.warning("switch_date...")
        # self.current_date = time.strftime(utils.kFormatFileDate)
        v = xtdata.get_market_last_trade_date('SH')
        local_time = time.localtime(v / 1000)
        trade_date = time.strftime(utils.kFormatFileDate, local_time)
        self.current_date = trade_date
        logger.warning("switch_date...{}", self.current_date)
        flag = 'head'
        self.t89k_flag_ready = os.path.join(self.order_path, f'{self.current_date}-{flag}.ready')
        self.t89k_flag_done = os.path.join(self.order_path, f'{self.current_date}-{flag}-{self.account_id}.done')
        self.t89k_order_file = os.path.join(self.order_path, f'{self.current_date}-{flag}.csv')
        self.positions_sell_done = os.path.join(self.order_path, f'{self.current_date}-sell-{self.account_id}.done')
        # qmt订单文件
        self.qmt_order_filename = os.path.join(self.order_path, f'{self.account_id}-orders.csv')
        self.qmt_order_done = os.path.join(self.order_path, f'{self.account_id}-orders-{self.current_date}.done')
        # qmt持仓文件
        self.qmt_positions_filename = os.path.join(self.order_path, f'{self.account_id}-positions.csv')

    def orders_has_refreshed(self) -> bool:
        """
        当日订单是否已经刷新完成
        :return:
        """
        return self.__filelock(self.qmt_order_done)

    def push_orders_refreshed(self):
        """
        标注订单刷新已完成
        :return:
        """
        self._push_local_message(self.qmt_order_done)

    def push_head_order_buy_completed(self):
        """
        买入操作完成
        :return:
        """
        self._push_local_message(self.t89k_flag_done)
        logger.info('订单买入操作完成')

    def head_order_buy_is_finished(self) -> bool:
        """
        早盘订单是否完成
        :return:
        """
        return os.path.isfile(self.t89k_flag_done)

    def push_positions_sell_completed(self):
        """
        标记卖出操作完成
        :return:
        """
        self._push_local_message(self.positions_sell_done)

    def positions_sell_finished(self):
        """
        卖出是否操作完成
        :return:
        """
        return os.path.isfile(self.positions_sell_done)

    def check_buy_order_done_status(self, code: str) -> bool:
        """
        检查买入订单执行完成状态
        :return:
        """
        flag = self.get_order_flag(code, order_buy)
        return os.path.exists(flag)

    def push_buy_order_done_status(self, code: str):
        """
        推送买入订单完成状态
        :param code:
        :return:
        """
        flag = self.get_order_flag(code, order_buy)
        self._push_local_message(flag)

    def _push_local_message(self, filename: str):
        """
        推送消息
        :param filename:
        :return:
        """
        with open(filename, 'w') as done_file:
            pass

    def get_order_flag(self, code: str, type: int) -> str:
        """
        获取订单标识
        :param self:
        :param code:
        :param type: 1-b(buy),2-s(ell),3-j(unk)
        :return:
        """
        today = time.strftime(utils.kFormatFileDate)
        if type == order_buy:
            order_flag = flag_buy
        elif type == order_sell:
            order_flag = flag_sell
        else:
            order_flag = flag_junk
        order_flag_path = self.order_path + "/var/" + today
        q1x_base.mkdirs(order_flag_path)
        stock_order_flag = os.path.join(order_flag_path, f'{today}-{self.account_id}-{code}-{order_flag}.done')
        return stock_order_flag

    def fix_security_code(self, symbol: str) -> str:
        """
        调整证券代码
        :param symbol:
        :return:
        """
        security_code = ''
        if len(symbol) == 6:
            flag = self.get_security_type(symbol)
            security_code = f'{symbol}.{flag}'
        elif len(symbol) == 8 and symbol[:2] in ["sh", "sz", "SH", "SZ"]:
            security_code = symbol[2:] + '.' + symbol[:2].upper()
        else:
            raise utils.errBadSymbol
        return security_code

    def get_security_type(self, symbol: str) -> str:
        """
        获取股票市场标识
        :param symbol:  代码
        :return:
        """
        if len(symbol) != 6:
            raise utils.errBadSymbol
        code_head = symbol[:2]
        if code_head in ["00", "30"]:
            return "SZ"
        if code_head in ["60", "68"]:  # 688XXX科创板
            return "SH"
        if code_head in ["510"]:
            return "SH"
        raise utils.errBadSymbol

    def __filelock(self, filename: str) -> bool:
        """
        文件锁状态
        :return:
        """
        return os.path.isfile(filename)
