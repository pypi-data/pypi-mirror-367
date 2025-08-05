# -*- coding: UTF-8 -*-
import math
import os
import time
from typing import Any

import pandas as pd
import q1x.base
import win32com.client
from pandas import DataFrame
from q1x.base import file
from xtquant import xtdata, xtconstant
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import *

from trader1x import utils
from trader1x.config import TraderConfig
from trader1x.context import QmtContext
from trader1x.log4py import logger

# 禁止显示XtQuant的hello信息
xtdata.enable_hello = False

def getuser():
    """
    获取用户名
    :return:
    """
    home = file.homedir()
    _, username = os.path.split(home)
    return username


# 缓存qmt安装路径
__gjzq_qmt_exec_path = ''


def get_gjzq_qmt_exec_path() -> str:
    """
    获取QMT安装路径
    """
    global __gjzq_qmt_exec_path
    if len(__gjzq_qmt_exec_path) > 0:
        return __gjzq_qmt_exec_path
    username = getuser()
    logger.info('user={}', username)
    qmt_exec_lnk = rf'C:\Users\{username}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\国金证券QMT交易端\启动国金证券QMT交易端.lnk'
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(qmt_exec_lnk)
    target_path = str(shortcut.Targetpath)
    paths = target_path.split(r'\bin.x64')
    exec_path = os.path.expanduser(paths[0])
    # exec_path = exec_path.replace('\\', '/')
    __gjzq_qmt_exec_path = exec_path
    return exec_path


class ThinkTrader(q1x.base.Singleton, XtQuantTraderCallback):
    """
    迅投XtQuant-miniQMT交易
    """
    __qmt_dir: str = None
    __xt_trader = None
    __account = None
    __config = None
    __running: bool = False

    def __init__(self, conf: TraderConfig):
        """
        初始化
        :param conf:
        """
        super().__init__()
        self.__config = conf
        self.__running = True
        # miniQMT session
        self.__miniqmt_session_id = 20221128

    def close(self):
        """
        析构方法, 销毁对象
        """
        self.stop_trader()
        logger.info("thinktrader shutdown")

    def stop_trader(self):
        self.__running = False
        if self.__xt_trader is not None:
            self.__xt_trader.stop()

    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        logger.error("connection lost, 交易接口断开，即将重连")
        self.stop_trader()

    def is_running(self) -> bool:
        """
        交易通道是否正常运行
        :return:
        """
        return self.__running

    def reconnect(self):
        """
        重连
        """
        if not self.__running:
            self.stop_trader()
            self.connect()

    def connect(self, qmt_dir: str = '') -> int:
        if self.__qmt_dir is None:
            qmt_dir.strip()
            if qmt_dir == '':
                qmt_dir = os.path.join(get_gjzq_qmt_exec_path(), 'userdata_mini')
                self.__qmt_dir = qmt_dir
        logger.info("miniQmt: {}", self.__qmt_dir)
        session_id = self.__miniqmt_session_id
        logger.info("session id: {}", session_id)
        self.__xt_trader = XtQuantTrader(self.__qmt_dir, session_id, self)
        # 启动交易线程
        self.__xt_trader.start()
        # 建立交易连接，返回0表示连接成功
        connect_result = self.__xt_trader.connect()
        logger.info("connect_result={}", connect_result)
        if connect_result == 0:
            self.__running = True
            logger.info('connect miniQmt: success')
            single_funds_available = self.single_available(self.__config.max_stock_quantity_for_strategy)
            logger.warning('今天, 单一策略最大可买{}个标的, 每标的可用金额{}',
                           self.__config.max_stock_quantity_for_strategy,
                           single_funds_available)
        else:
            self.__running = False
            self.__xt_trader.stop()
            self.__xt_trader = None
            logger.error('connect miniQmt: failed')
        return connect_result

    def set_account(self, account_id, account_type='STOCK'):
        self.__account = StockAccount(account_id, account_type=account_type)
        return self.__account

    @property
    def get_account(self):
        return self.__account

    @property
    def get_trader(self):
        return self.__xt_trader

    def query_asset(self) -> XtAsset:
        """
        获取资产数据
        :return:
        """
        return self.__xt_trader.query_stock_asset(self.get_account)

    def account_available(self) -> tuple[float, float]:
        """
        可用资金
        :return:
        """
        asset = self.query_asset()
        if asset is None:
            return 0.00, 0.00
        return asset.total_asset, asset.cash

    def asset_can_trade(self) -> bool:
        """
        资产是否可交易
        :return:
        """
        _, available = self.account_available()
        return available > self.__config.keep_cash

    def single_available(self, num: int) -> float:
        """
        调整单一可用资金
        :param num: 股票数量
        :return:
        """
        if num < 1:
            return 0.00
        # 1. 查询 总资产和可用
        acc_total, acc_cash = self.account_available()
        # 2. 查询持仓可卖的股票, TODO: y如果确定了可卖出的市值, 怎么保证当日必须卖出?
        positions = self.query_positions()
        can_use_amount = 0.00
        # 3. 设置一个可卖股票的市值波动范围, 这里暂定10%
        vix = 0.10
        acc_value = 0.00  # 总市值
        for position in positions:
            acc_value += position.market_value
            if position.can_use_volume < 1:
                continue
            # 计算现价
            market_price = position.market_value / position.volume
            # 累计可卖的市值: 可卖数量 * 市价
            can_use_value = position.can_use_volume * market_price
            can_use_amount += can_use_value * (1 - vix)
        acc_value = q1x.base.float_round(acc_value)
        if acc_total == 0:
            # qmt有一定概率出现总资金为0的情况
            acc_total = acc_value
        can_use_amount = q1x.base.float_round(can_use_amount)
        # 4. 确定可用资金总量: 账户可以资金 + 当日可卖出的总市值 - 预留现金
        can_use_cash = acc_cash + can_use_amount - self.__config.keep_cash
        # 5. 计算预留仓位, 给下一个交易日留position_ratio仓位
        reserve_cash = q1x.base.float_round(acc_total * self.__config.position_ratio)
        # 6. 计算当日可用仓位: 可用资金总量 - 预留资金总量
        available = can_use_cash - reserve_cash
        logger.warning('账户资金, 可用: {}, 市值: {}, 预留: {}, 可买: {}, 可卖: {}', acc_cash, acc_value, reserve_cash,
                       available, can_use_amount)
        # 7. 如果当日可用金额大于资金账户的可用金额, 输出风险提示
        if available > acc_cash:
            logger.warning(
                '!!! 持仓占比[{}%], 已超过可总仓位的[{}%], 必须在收盘前择机降低仓位, 以免影响下一个交易日的买入操作 !!!',
                q1x.base.float_round(100 * (acc_value / acc_total)),
                q1x.base.float_round(100 * (1 - self.__config.position_ratio)))
        # 8. 计算单一标的可用资金
        single_funds_available = q1x.base.float_round(available / num)
        # 9. 检查可用资金的最大值和最小值
        if single_funds_available > self.__config.buy_amount_max:
            single_funds_available = self.__config.buy_amount_max
        elif single_funds_available < self.__config.buy_amount_min:
            return 0.00
        return single_funds_available

    def available_amount(self, stock_num: int) -> float:
        """
        计算单一标的可用金额
        :param stock_num: 股票总数
        :return:
        """
        single_funds_available = self.single_available(stock_num)
        if single_funds_available <= self.__config.buy_amount_min:
            return 0.00
        return single_funds_available

    def available_amount_for_tick(self, stock_num: int) -> float:
        """
        计算单一标的可用金额
        :param stock_num: 股票总数
        :return:
        """
        single_funds_available = self.available_amount(stock_num)
        if single_funds_available <= self.__config.tick_order_min_amount:
            return 0.00
        if single_funds_available > self.__config.tick_order_max_amount:
            # 超出单个标的最大买入金额, 按照最大金额来处理
            single_funds_available = self.__config.tick_order_max_amount
        return single_funds_available

    def get_snapshot(self, security_code: str = '') -> Any:
        """
        获得快照
        :param security_code:
        :return:
        """
        tick_list = xtdata.get_full_tick([security_code])
        if len(tick_list) != 1:
            return None
        snapshot = tick_list[security_code]
        return snapshot

    def available_price(self, price: float) -> float:
        """
        计算适合的买入价格
        :param price:
        :return:
        """
        lastPrice = price
        # 价格笼子, +2%和+0.10哪个大
        buy_price = max(lastPrice * 1.02, lastPrice + 0.10)
        # 当前价格+0.05
        # buy_price = snapshot['askPrice'][0] + 0.05
        buy_price = lastPrice + 0.05
        # 最后修订价格
        buy_price = q1x.base.float_round(buy_price)
        return buy_price

    def calculate_buy_fee(self, price: float, volume: int) -> float:
        """
        计算买入的总费用
        :return: 股票数量
        """
        # 1. 印花税, 按照成交金额计算, 买入没有, 卖出, 0.1%
        _stamp_duty_fee = q1x.base.float_round(volume * price * self.__config.stamp_duty_rate_for_buy)
        # 2. 过户费, 按照股票数量, 双向, 0.06%
        _transfer_fee = q1x.base.float_round(volume * self.__config.transfer_rate)
        # 3. 券商佣金, 按照成交金额计算, 双向, 0.025%
        _commission_fee = q1x.base.float_round(volume * price * self.__config.commission_rate)
        if _commission_fee < self.__config.commission_min:
            _commission_fee = self.__config.commission_min
        # 4. 股票市值
        _stock_fee = q1x.base.float_round(volume * price)
        _fee = (_stamp_duty_fee + _transfer_fee + _commission_fee + _stock_fee)
        logger.debug('综合费用:{}, 委托价格={}, 数量={}, 其中印花说={}, 过户费={}, 佣金={}, 股票={}', _fee, price,
                     volume, _stamp_duty_fee, _transfer_fee, _commission_fee, _stock_fee)
        return _fee

    def calculate_stock_volumes(self, fund: float, price: float) -> int:
        """
        可以购买的股票数量(股)
        :return: 股票数量
        """
        # 1. 印花税, 按照成交金额计算, 买入没有, 卖出, 0.1%
        # stamp_duty = volume * price * stamp_duty_rate
        _stamp_duty_fee = price * self.__config.stamp_duty_rate_for_buy
        # 2. 过户费, 按照股票数量, 双向, 0.06%
        # transfer_fee = volume * transfer_rate
        _transfer_fee = self.__config.transfer_rate
        # 3. 券商佣金, 按照成交金额计算, 双向, 0.025%
        # commissions = volume * price * commission_rate
        _commission_fee = price * self.__config.commission_rate
        # 4. 股票市值
        # _stock_fee= volume * price
        _stock_fee = price
        _fee = (_stamp_duty_fee + _transfer_fee + _commission_fee + _stock_fee)
        volume = fund / _fee
        volume = math.floor(volume / 100) * 100
        # 5. 检查买入总费用, 如果大于预计金额, 则减去100股
        _fee = self.calculate_buy_fee(price, volume)
        if _fee > fund:
            volume = volume - 100
        return volume

    def head_order_can_trade(self) -> bool:
        """
        早盘订单是否可交易
        :return:
        """
        return self.__config.head_time.is_trading()

    def tick_order_can_trade(self) -> bool:
        """
        检查盘中订单是否可以交易
        :return:
        """
        return self.__config.tick_time.is_trading()

    def tick_order_is_ready(self) -> bool:
        """
        盘中订单是否就绪
        :return:
        """
        return True

    def current_date(self) -> tuple[str, str]:
        """
        今天
        :return:
        """
        today = time.strftime(utils.kFormatOnlyDate)
        v = xtdata.get_market_last_trade_date('SH')
        local_time = time.localtime(v / 1000)
        trade_date = time.strftime(utils.kFormatOnlyDate, local_time)
        return today, trade_date

    def today_is_trading_date(self) -> bool:
        """
        今天是否交易日
        :return:
        """
        (today, trade_date) = self.current_date()
        logger.info('today={}, trade_date={}', today, trade_date)
        return today == trade_date

    def order_can_cancel(self) -> bool:
        """
        委托订单可以撤销
        :return:
        """
        return self.__config.cancel_time.is_trading()

    def order(self, code: str, order_type: int, order_volume: int, price_type: int, price: float,
              strategy_name: str = '', order_remark: str = '') -> int:
        """
        下单
        :param code: 证券代码, 例如"600000.SH"
        :param order_type: 委托类型, 23:买, 24:卖
        :param order_volume: 委托数量, 股票以'股'为单位, 债券以'张'为单位
        :param price_type: 报价类型, 详见帮助手册
        :param price: 报价价格, 如果price_type为指定价, 那price为指定的价格, 否则填0
        :param strategy_name: 策略名称
        :param order_remark: 委托备注, 极简客户端的order_remark字段有长度限制，最大23个英文字符(一个中文占3个), 超出的部分会丢弃,大qmt没有长度限制
        :return: 返回下单请求序号, 成功委托后的下单请求序号为大于0的正整数, 如果为-1表示委托失败
        """
        order_id = self.__xt_trader.order_stock(self.__account, code, order_type, order_volume, price_type, price,
                                                strategy_name, order_remark)
        return order_id

    def cancel(self, order_id: int) -> int:
        """
        撤单
        :param order_id:
        :return: 返回撤单成功或者失败, 0:成功, -1:委托已完成撤单失败, -2:未找到对应委托编号撤单失败, -3:账号未登陆撤单失败
        """
        return self.__xt_trader.cancel_order_stock(self.__account, order_id)

    def buy(self, code: str, price: float, vol: int, strategy_name: str = '', order_remark: str = '') -> int:
        """
        同步下买单
        """
        order_id = self.order(code, xtconstant.STOCK_BUY, vol, xtconstant.FIX_PRICE, price, strategy_name, order_remark)
        return order_id

    def sell(self, position: XtPosition, strategy_name: str = '', order_remark: str = '') -> int:
        """
        同步下卖单
        """
        order_id = self.order(position.stock_code, xtconstant.STOCK_SELL, position.can_use_volume,
                              xtconstant.LATEST_PRICE, -1, strategy_name, order_remark)
        return order_id

    def query_positions(self) -> list[XtPosition]:
        """
        查询持仓
        :return:
        """
        positions = self.__xt_trader.query_stock_positions(self.__account)
        return positions

    def query_trades(self) -> list[XtTrade]:
        """
        查询当日成交
        TODO: 历史成交暂时不支持
        :return:
        """
        trades = self.__xt_trader.query_stock_trades(self.__account)
        return trades

    def profit_and_loss(self, ctx: QmtContext):
        """
        盈亏统计
        :return:
        """
        positions = self.query_positions()
        if len(positions) == 0:
            return
        head = positions[0]
        keys = [key for key in dir(head) if not key.startswith('__')]
        df = pd.DataFrame([[getattr(e, key) for key in keys] for e in positions], columns=keys)
        if len(df) > 0:
            df.to_csv(ctx.qmt_positions_filename, encoding='utf-8', index=False)

    def query_orders(self, cancelable_only: bool = False) -> list[XtOrder]:
        """
        查询委托
        :return:
        """
        orders = self.__xt_trader.query_stock_orders(self.__account, cancelable_only)
        return orders

    def query_order(self, order_id: int) -> XtOrder:
        """
        查询单一委托
        :return:
        """
        order = self.__xt_trader.query_stock_order(self.__account, order_id)
        return order

    def refresh_order(self) -> DataFrame | None:
        """
        刷新委托订单
        :return:
        """
        orders = self.query_orders()
        if len(orders) == 0:
            return
        head = orders[0]
        keys = [key for key in dir(head) if not key.startswith('__')]
        df = pd.DataFrame([[getattr(e, key) for key in keys] for e in orders], columns=keys)
        if len(df) > 0:
            # 修改订单字段, 将秒数改为时间戳字符串
            key_time = 'order_time'
            df[key_time] = df[key_time].apply(lambda x: time.strftime(utils.kFormatTimestamp, time.localtime(x)))
            df = self.align_fields_for_order(df)
        return df

    def align_fields_for_order(self, df: DataFrame) -> DataFrame:
        """
        对齐 订单字段
        :param df:
        :return:
        """
        # account_id: 资金账号
        # stock_code: 证券代码, 例如"600000.SH"
        # order_id: 委托编号
        # order_sysid: 柜台编号
        # order_time: 报单时间
        # order_type: 委托类型, 23:买, 24:卖
        # order_volume: 委托数量, 股票以'股'为单位, 债券以'张'为单位
        # price_type: 报价类型, 详见帮助手册
        # price: 报价价格，如果price_type为指定价, 那price为指定的价格，否则填0
        # traded_volume: 成交数量, 股票以'股'为单位, 债券以'张'为单位
        # traded_price: 成交均价
        # order_status: 委托状态
        # status_msg: 委托状态描述, 如废单原因
        # strategy_name: 策略名称
        # order_remark: 委托备注
        cols = ['order_time', 'strategy_name', 'order_remark', 'order_type', 'stock_code', 'price_type', 'price',
                'traded_price', 'order_status', 'status_msg', 'order_volume', 'traded_volume', 'account_id', 'order_id',
                'order_sysid']
        df = df[cols]
        return df

    def total_strategy_orders(self, strategy_code: int) -> int:
        """
        统计策略订单数量
        :return:
        """
        df = self.refresh_order()
        if len(df) == 0:
            return 0
        # print(df)
        condition = (df['order_remark'] == 'tick') & (df['strategy_name'] == f'S{strategy_code}')
        df = df[condition]
        return len(df)
