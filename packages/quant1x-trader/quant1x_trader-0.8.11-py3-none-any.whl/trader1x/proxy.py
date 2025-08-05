# -*- coding: UTF-8 -*-
import signal

import q1x
import xtquant.xtdata
from q1x import base
from q1x.base import market

module = 'trader1x'

base.redirect(module, __file__)

import sys
from path import Path
from fastapi import FastAPI, Form
from xtquant import xtconstant

from trader1x import thinktrader, config, utils, context
from trader1x.log4py import logger, quant1x_data_path

# 禁止显示XtQuant的hello信息
xtquant.xtdata.enable_hello = False
__application_proxy = 'quant1x-proxy'

order_status = {
    xtconstant.ORDER_UNREPORTED: '未报',
    xtconstant.ORDER_WAIT_REPORTING: '待报',
    xtconstant.ORDER_REPORTED: '已报',
    xtconstant.ORDER_REPORTED_CANCEL: '已报待撤',
    xtconstant.ORDER_PARTSUCC_CANCEL: '部成待撤',
    xtconstant.ORDER_PART_CANCEL: '部撤',
    xtconstant.ORDER_CANCELED: '已撤',
    xtconstant.ORDER_PART_SUCC: '部成',
    xtconstant.ORDER_SUCCEEDED: '已成',
    xtconstant.ORDER_JUNK: '废单',
    xtconstant.ORDER_UNKNOWN: '未知'
}

# 操作 - 状态码 - 成功
OPERATION_STATUS_SUCCESS = 0
# 操作 - 信息 - 成功
OPERATION_MESSAGE_SUCCESS = 'success'
# 操作 - 状态码 - 未知
OPERATION_STATUS_UNKNOWN = 999
# 操作 - 信息 - 未知
OPERATION_MESSAGE_UNKNOWN = 'unknown'

__uri_prefix = '/qmt'
app = FastAPI(root_path=__uri_prefix)


def trader_reconnect():
    """
    交易通道重连
    """
    global __context, __trader, __config
    ctx_need_init = __trader.is_running()
    __trader.reconnect()
    if not ctx_need_init and __trader.is_running():
        __context = context.QmtContext(__config)


from apscheduler.schedulers.background import BackgroundScheduler

# 1.1
__scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
__scheduler.add_job(trader_reconnect, trigger='interval', seconds=10)
__scheduler.start()


@app.on_event('startup')
async def proxy_init():
    """
    代理初始化
    :return:
    """
    # global __config
    global __context, __trader, __config
    logger.info('{} start...', __application_proxy)
    # 1. 获取配置信息
    __config = config.load()
    __trader = thinktrader.ThinkTrader(__config)
    # 2. 设置账号
    # __context = context.QmtContext(__config)
    __trader.set_account(__config.account_id)

    # # 1.1
    # __scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    # __scheduler.add_job(trader_reconnect, trigger='interval', second=10)
    # __scheduler.start()
    # 3. 连接miniQMT
    connect_result = __trader.connect()
    if connect_result == 0:
        logger.info('connect miniQmt: success')
    else:
        logger.error('connect miniQmt: failed')
        return utils.errno_miniqmt_connect_failed
    logger.info('{} start...OK', __application_proxy)
    # 4. 设置账号
    __context = context.QmtContext(__config)
    return None


@app.on_event('shutdown')
async def proxy_shutdown():
    """
    代理关闭
    :return:
    """
    logger.info('{} shutdown...', __application_proxy)
    __trader.close()
    logger.info('{} shutdown...OK', __application_proxy)


@app.api_route('/health')
async def hello(name: str = 'anonymous'):
    """
    探测服务接口(√)
    :param name:
    :return:
    """
    return {rf'hello, {name}'}


@app.api_route('/data/subscribe_whole_quote')
async def data_subscribe_whole_quote(code: str = 'SH,SZ'):
    """
    订阅全推行情
    :param code:
    :return:
    """
    code_list = code.split(",")
    data = xtquant.xtdata.subscribe_whole_quote(code_list)
    return {'status': OPERATION_STATUS_SUCCESS, 'message': OPERATION_MESSAGE_SUCCESS, 'seq': data}


@app.api_route('/data/unsubscribe_quote')
async def data_unsubscribe_quote(seq: str = ''):
    """
    反订阅行情数据
    :param seq: 订阅号
    :return:
    """
    seq_id = int(seq)
    data = xtquant.xtdata.unsubscribe_quote(seq_id)
    return data


@app.api_route('/data/tick')
async def data_full_tick(code: str = 'SH,SZ'):
    """
    获取tick(√)
    :param code:
    :return:
    """
    code_list = code.split(",")
    data = xtquant.xtdata.get_full_tick(code_list)
    return data


@app.api_route('/query/asset', methods=['GET', 'POST'])
async def query_assets():
    """
    查询总资产(√)
    """
    asset = __trader.query_asset()
    return {"total_asset": asset.total_asset,
            "cash": asset.cash,
            "market_value": asset.market_value,
            "frozen_cash": asset.frozen_cash
            }


@app.api_route('/query/holding', methods=['GET', 'POST'])
async def query_holding():
    """
    查询当前持仓(√)
    """
    holding = []
    for p in __trader.query_positions():
        holding.append(
            {'account_type': p.account_type,
             'account_id': p.account_id,
             'stock_code': p.stock_code,
             'volume': p.volume,
             'can_use_volume': p.can_use_volume,
             'open_price': q1x.base.fix_float(p.open_price),
             'market_value': q1x.base.fix_float(p.market_value),
             'frozen_volume': p.frozen_volume,
             'on_road_volume': p.on_road_volume,
             'yesterday_volume': p.yesterday_volume,
             'avg_price': q1x.base.fix_float(p.avg_price),
             }
        )
    return holding


@app.api_route('/query/trade', methods=['GET', 'POST'])
async def query_trade():
    """
    查询当日成交(√)
    """
    trades = __trader.query_trades()
    result = []
    for trade in trades:
        result.append(
            {'stock_code': trade.stock_code,
             'order_type': trade.order_type,
             'traded_volume': trade.traded_volume,
             'traded_price': trade.traded_price,
             'traded_amount': trade.traded_amount,
             'traded_time': q1x.base.seconds_to_timestamp(trade.traded_time),
             "traded_id": trade.traded_id, "order_sysid": trade.order_sysid})
    return result


@app.api_route('/query/order', methods=['GET', 'POST'])
async def query_order(order_id: str = ''):
    """
    查询当日委托(√)
    :param order_id: 订单id
    """
    order_id = order_id.strip()
    if order_id == '' or order_id == '0':
        orders = __trader.query_orders()
    else:
        order = __trader.query_order(int(order_id))
        # 订单不存在，下单失败
        if order is None:
            return []
        orders = [order]
    result = []
    for order in orders:
        result.append(
            {'account_type': order.account_type,
             'account_id': order.account_id,
             'order_time': q1x.base.seconds_to_timestamp(order.order_time),
             'stock_code': order.stock_code,
             'order_type': order.order_type,
             'price': order.price,
             'price_type': order.price_type,
             'order_volume': order.order_volume,
             'order_id': order.order_id,
             "order_sysid": order.order_sysid,
             'traded_price': order.traded_price,
             'traded_volume': order.traded_volume,
             'order_status': order.order_status,
             'status_msg': order.status_msg,
             'strategy_name': order.strategy_name,
             'order_remark': order.order_remark,
             }
        )
    return result


def throw_error(status: int, message: str) -> dict:
    """
    抛出错误
    :param status: 状态码, 0-成功, 非0-失败
    :param message: 错误信息
    :return:
    """
    return {'status': status, 'message': message}


@app.api_route('/trade/order', methods=['POST'])
async def trade_place_order(direction: str = Form(''),
                            code: str = Form(''),
                            price_type: str = Form(''),
                            price: str = Form(''),
                            volume: str = Form(''),
                            strategy: str = Form(''),
                            remark: str = Form('')
                            ):
    """
    下单(√), 参数有:
    direction: 交易方向, buy, sell
    code: 证券代码, 格式:{code}.{marker_id}
    price_type: 报价类型
    price: 价格, 单位是元
    volume: 数量, 单位是股
    strategy: 策略名称
    remark: 订单备注
    """
    order_errno = 10000
    status = OPERATION_STATUS_SUCCESS
    message = OPERATION_MESSAGE_SUCCESS
    # 1. 交易方向
    direction = direction.strip()
    if direction == 'buy':
        # 1.1 买入
        trade_direction = xtconstant.STOCK_BUY
    elif direction == 'sell':
        # 1.2 卖出
        trade_direction = xtconstant.STOCK_SELL
    else:
        # 1.3 方向错误
        return throw_error(order_errno + 10, '交易方向错误')
    # 2. 证券代码
    code = code.strip()
    if code == '':
        return throw_error(order_errno + 20, '证券代码不能为空')
    elif len(code) != 9:
        return throw_error(order_errno + 21, '非A股证券代码长度')
    elif not code.endswith(market.tup_market):
        return throw_error(order_errno + 22, '交易所简写错误')
    stock_code = code
    # 3. 报价类型
    price_type = price_type.strip()
    if price_type == '':
        return throw_error(order_errno + 30, '报价类型不能为空')
    stock_price_type = int(price_type)
    if stock_price_type != xtconstant.FIX_PRICE and stock_price_type != xtconstant.LATEST_PRICE:
        return throw_error(order_errno + 30, '报价类型必须是最新价或限价')
    # 4. 价格
    price = price.strip()
    if price == '':
        return throw_error(order_errno + 40, '委托价格不能为空')
    stock_price = float(price)
    if stock_price <= 1.000:
        return throw_error(order_errno + 41, '委托价格不能出现小于等于1.000元')
    # 5. 数量
    volume = volume.strip()
    if volume == '':
        return throw_error(order_errno + 50, '交易数量不能为空')
    stock_volume = int(volume)
    if stock_volume % 100 != 0:
        return throw_error(order_errno + 51, '交易数量非100股的整数倍')
    # 6. 策略名称
    strategy = strategy.strip()
    if strategy == '':
        return throw_error(order_errno + 60, '策略名称不能为空')
    strategy_name = strategy
    # 7. 订单备注
    remark = remark.strip()
    if remark == '':
        return throw_error(order_errno + 70, '订单备注不能为空')
    if len(remark.encode('utf-8')) > 24:
        return throw_error(order_errno + 71, '订单备注不能超过24个字节')
    order_remark = remark
    # 8. 执行同步委托下单
    order_id = __trader.order(stock_code, trade_direction, stock_volume, stock_price_type, stock_price,
                              strategy_name, order_remark)
    logger.warning('order[{}]: code={}, direction={}, price={}, volume={}, strategy_name={}, order_remark={}', order_id,
                   stock_code, direction, stock_price, stock_volume, strategy_name, order_remark)
    return {'status': status, 'message': message, 'order_id': order_id}


@app.api_route('/trade/cancel', methods=['POST'])
async def trade_cancel_order(order_id: str = Form('')):
    """
    撤单(√)
    """
    cancel_errno = 20000
    order_id = order_id.strip()
    if order_id == '':
        return throw_error(cancel_errno + 1, 'order_id不能为空')
    elif not order_id.isdigit():
        return throw_error(cancel_errno + 2, 'order_id必须是整型')
    cancel_order_id = int(order_id)
    if cancel_order_id <= 0:
        return throw_error(cancel_errno + 3, 'order_id必须大于0')
    result = __trader.cancel(cancel_order_id)
    logger.warning(f'order_id={order_id}, errno={result}')
    # 返回撤单成功或者失败, 0: 成功, -1: 委托已完成, -2: 未找到对应委托编号, -3: 账号未登陆
    if result == 0:
        return throw_error(OPERATION_STATUS_SUCCESS, OPERATION_MESSAGE_SUCCESS)
    elif result == -1:
        return throw_error(cancel_errno + 4, '委托已完成')
    elif result == -2:
        return throw_error(cancel_errno + 5, '未找到对应委托编号')
    elif result == -3:
        return throw_error(cancel_errno + 6, '账号未登陆')
    else:
        logger.warning(f'cancel: order_id={order_id}, 未知错误, errno={result}')
    return throw_error(cancel_errno + OPERATION_STATUS_UNKNOWN, OPERATION_MESSAGE_UNKNOWN)


def sign(enable: bool = True):
    """
    验签 - 函数装饰器(aspect)
    TODO: 具体验签方式未完成
    :param enable: 是否启用验签, 默认启用验签
    :return:
    """

    def count_time(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return count_time


def proxy_exit(signum, frame):
    """
    退出前操作
    :param signum:
    :param frame:
    :return:
    """
    global trader
    logger.info('{} shutdown...', __application_proxy)
    proxy_stop()
    logger.info('{} shutdown...OK', __application_proxy)
    sys.exit(0)


def proxy_start() -> int:
    """
    启动代理
    :return:
    """
    import uvicorn.server
    import contextlib

    # 替代 capture_signals 上下文管理器
    @contextlib.contextmanager
    def nop_handler(*args, **kwargs):
        yield  # 必须要有 yield 才能作为上下文管理器使用

    uvicorn.server.Server.capture_signals = nop_handler  # 禁用信号处理

    global web_server
    # signal.signal(signal.SIGINT, proxy_exit)
    # signal.signal(signal.SIGTERM, proxy_exit)
    # 1. 加载配置文件
    # logger.add('d:\proxy.log', rotation='00:00')
    logger.info('加载配置...')
    __config = config.load()
    logger.info('配置信息: {}', __config)
    logger.info('加载配置...OK')
    # 2. 配置路由
    # app.include_router(prefix=__uri_prefix)
    # 3. 启动服务
    logger.warning('{} start http server[{}:{}]...', __application_proxy, __config.proxy_address, __config.proxy_port)
    # uvicorn.run(app=f'{module}.{Path(__file__).stem}:app', host=__config.proxy_address, port=__config.proxy_port,
    #             workers=__config.proxy_workers,
    #             reload=False, debug=True)
    # uvicorn.run(app='trader1x.proxy:app', host=__config.proxy_address, port=__config.proxy_port,
    #             workers=__config.proxy_workers,
    #             reload=False, debug=True)

    log_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "handlers": {
            "file_handler": {
                "class": "logging.FileHandler",
                "filename": f'{quant1x_data_path}/logs/logfile.log',
            },
        },
        "root": {
            "handlers": ["file_handler"],
            "level": "INFO",
        },
    }

    cfg = uvicorn.Config(app=f'{module}.{Path(__file__).stem}:app', host=__config.proxy_address,
                         port=__config.proxy_port,
                         workers=__config.proxy_workers,
                         log_config=log_config,
                         # 添加以下参数：
                         # capture_signals=False,  # 关键参数：禁用信号捕获
                         )
    web_server = uvicorn.Server(config=cfg)
    # According to https://github.com/encode/uvicorn/issues/526, on Python 3.8+ you MIGHT also need:
    # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # But in my case it didn't seem to be necessary
    web_server.install_signal_handlers = lambda: None  # this is the necessary workaround
    web_server.run()
    return 0


def proxy_stop():
    """
    关闭代理
    :return:
    """
    global web_server
    # web_server.shutdown()
    try:
        # web_server.shutdown()
        web_server.should_exit = True
        web_server.shutdown()
    except Exception as e:
        logger.exception(e)


import socket
import servicemanager
import win32event
import win32service
from trader1x import win32serviceutil

cmd_service = 'service'


class ProxyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'quant1x-qmt-proxy'
    _svc_display_name_ = 'Quant1X-miniQMT-Proxy'
    _svc_description_ = 'Quant1X miniQMT 代理服务'
    _exe_args_ = cmd_service

    def __init__(self, args):
        """
        Constructor of the winservice
        """
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        """
        Called when the service is asked to stop
        """
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """
        Called when the service is asked to start
        """
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        """
        Override to add logic before the start
        eg. running condition
        """
        self.is_alive = True

    def stop(self):
        """
        Override to add logic before the stop
        eg. invalidating running condition
        """
        self.is_alive = False
        proxy_stop()

    def main(self):
        """
        Main class to be overridden to add logic
        """
        try:
            proxy_start()
        except Exception as e:
            logger.exception(e)


def main() -> int:
    argv = sys.argv
    argc = len(argv)
    if argc <= 1:
        # 直接启动proxy
        signal.signal(signal.SIGINT, proxy_exit)
        signal.signal(signal.SIGTERM, proxy_exit)
        ret = proxy_start()
    elif argv[1] == cmd_service:
        argv.remove(cmd_service)
        if len(argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(ProxyService)
            servicemanager.StartServiceCtrlDispatcher()
            ret = 0
        else:
            ret = win32serviceutil.HandleCommandLine(ProxyService, argv=argv)
    else:
        print('usage: quant1x-qmt-proxy')
        print('       quant1x-qmt-proxy service [install|remove|start|stop|restart]')
        ret = 0
    return ret


if __name__ == '__main__':
    sys.exit(main())
