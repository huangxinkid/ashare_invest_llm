import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

filter_executor = ThreadPoolExecutor(max_workers=2)


async def async_stock_zh_a_spot_em():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(filter_executor, ak.stock_zh_a_spot_em, )
    return result


# 定义“神奇九转”指标筛选逻辑
def is_magic_9_turns(stock_code, period=9):
    """
    判断某只股票是否符合“神奇九转”上涨条件
    :param stock_code: 股票代码
    :param period: 周期，默认为 9
    :return: 是否符合“神奇九转”条件
    """
    # 获取该股票的历史数据
    today = datetime.today()
    start_date = (today - timedelta(days=20)).strftime('%Y%m%d')
    end_date = today.strftime('%Y%m%d')
    stock_hist = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq", start_date=start_date, end_date=end_date)
    
    # 计算涨跌幅
    stock_hist['涨跌幅'] = stock_hist['收盘'].pct_change() * 100
    
    # 筛选出涨幅大于 0 的周期
    rising_periods = stock_hist[stock_hist['涨跌幅'] > 0]
    
    # 如果涨幅周期不足 period 次，直接返回 False
    if len(rising_periods) < period:
        return False
    
    # 获取前 period 次涨幅
    top_n_rises = rising_periods.head(period)
    
    # 计算前 8 次涨幅的平均值
    avg_rise = top_n_rises['涨跌幅'].iloc[:-1].mean()
    
    # 获取第 9 次涨幅
    ninth_rise = top_n_rises['涨跌幅'].iloc[-1]
    
    # 判断第 9 次涨幅是否超过前 8 次的平均涨幅
    return ninth_rise > avg_rise


async def get_need_ticker():
    # 获取沪深京 A 股实时行情数据
    stock_data = await async_stock_zh_a_spot_em()

    # 筛选出涨幅大于 0 的股票
    rising_stocks = stock_data[stock_data['涨跌幅'] > 5]
    # 应用“神奇九转”指标筛选
    selected_stocks = []
    for stock in rising_stocks.itertuples():
        try:
            stock_code = stock.代码
            stock_name = stock.名称
            if stock.换手率 >=20 or stock.换手率 <10:
                continue
            if stock.最新价 >=100 or stock.最新价 <5:
                continue
            if not is_magic_9_turns(stock_code):
                continue
            selected_stocks.append(
                {'code': stock_code, 'name': stock_name,
                 'status': 'running', 'action': '', 'result': ''})
        except Exception as e:
            print(f"处理股票 {stock_code} 时出错: {e}")

    # 打印结果
    print("符合‘神奇九转’上涨条件的股票代码：")
    return selected_stocks


if __name__ == '__main__':
    ret = asyncio.run(get_need_ticker())
    print(ret)
