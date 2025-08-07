# -*- coding: utf-8 -*-
from datetime import datetime
from .stock_data import get_etf_data, get_stock_hist_data, calculate_rsi, calculate_atr, calculate_bollinger_bands, calculate_moving_averages, classify_market_style
from .etf_screener import screen_etf_anomaly, screen_etf_anomaly_cached
from mcp.server.fastmcp import FastMCP
import pandas as pd

import sys
sys.stdout.reconfigure(encoding='utf-8')

mcp = FastMCP()


#@mcp.resource("data://etf/{etf_code}/indicators.md?with_market_style={with_market_style}&base_date={base_date}")
@mcp.tool(name="analyze_etf_technical", description="分析ETF技术指标，包括RSI、布林带、移动平均线等")
def analyze_etf_technical(etf_code='510300', with_market_style: bool=True, base_date: str=None, return_days: int=5, return_format: str='markdown'):
    """
    ETF技术指标分析工具，获取包括价格、RSI(10日)、布林带等关键指标
    :param etf_code: ETF代码 (例如'510300') 不要使用LOF代码
    :param with_market_style: 是否对市场风格进行分类 (True/False)
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param return_days: 返回最后几条数据 (默认为5条)
    :param return_format: 返回数据格式 (默认为markdown，可选为json)
    :return: 包含技术指标的DataFrame (Markdown格式)
    
    返回数据示例:
    | date       | close | rsi_10 | boll_upper | boll_middle | boll_lower | ma_5 | ma_10 | ma_20 | volume |
    |------------|-------|--------|------------|-------------|------------|------|-------|-------|--------|
    | 2023-01-01 | 4.12  | 65.32  | 4.25       | 4.10        | 3.95       | 4.08 | 4.05  | 4.02  | 120000 |
    
    字段说明:
    - date: 交易日期
    - close: 收盘价
    - rsi_10: 10日相对强弱指数(30-70为正常区间)
    - boll_upper: 布林带上轨(20日平均+2倍标准差)
    - boll_middle: 布林带中轨(20日移动平均)
    - boll_lower: 布林带下轨(20日平均-2倍标准差)
    - ma_5: 5日移动平均
    - ma_10: 10日移动平均
    - ma_20: 20日移动平均
    - atr: 平均真实波幅(10日)，衡量价格波动性的指标
    - mkt_style: 市场风格分类结果
    - volume: 成交量(单位:份)，反映市场活跃度，高成交量通常伴随价格趋势确认
    """
    # 判断base_date是否为None
    df = get_etf_data(etf_code=etf_code, end_date=base_date, duration=90+return_days)
    
    if df is not None:
        # 计算技术指标
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        
        # 如果需要进行市场风格分类
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        # 返回最后return_days条数据
        if return_format == 'markdown':
            return df.tail(return_days).to_markdown()
        else:
            return df.tail(return_days).to_dict(orient='records')
    else:
        raise Exception(f"无法获取数据，请检查输入参数{etf_code}是否正确。 ")


#@mcp.resource("data://stock/{stock_code}/indicators.md?with_market_style={with_market_style}&base_date={base_date}")
@mcp.tool(name="analyze_stock_hist_technical", description="分析股票历史数据技术指标，包括RSI、布林带、移动平均线等")
def analyze_stock_hist_technical(stock_code='000001', with_market_style: bool=True, base_date: str=None, return_days: int=5, return_format: str='markdown'):
    """
    股票历史数据技术指标分析工具，获取包括价格、RSI(10日)、布林带等关键指标
    :param stock_code: 股票代码 (例如'000001')
    :param with_market_style: 是否对市场风格进行分类 (True/False)
    :param base_date: 基准日期(格式YYYYMMDD)，默认为当前日期
    :param return_days: 返回最后几条数据 (默认为5条)
    :param return_format: 返回数据格式 (默认为markdown，可选为json)
    :return: 包含技术指标的DataFrame (Markdown格式)
    
    返回数据示例:
    | date       | close | rsi_10 | boll_upper | boll_middle | boll_lower | ma_5 | ma_10 | ma_20 | volume |
    |------------|-------|--------|------------|-------------|------------|------|-------|-------|--------|
    | 2023-01-01 | 12.45 | 58.76  | 12.80      | 12.40       | 12.00      | 12.38| 12.35 | 12.30 | 45000  |
    
    字段说明:
    - date: 交易日期
    - close: 收盘价
    - rsi_10: 10日相对强弱指数(30-70为正常区间)
    - boll_upper: 布林带上轨(20日平均+2倍标准差)
    - boll_middle: 布林带中轨(20日移动平均)
    - boll_lower: 布林带下轨(20日平均-2倍标准差)
    - ma_5: 5日移动平均
    - ma_10: 10日移动平均
    - ma_20: 20日移动平均
    - atr: 平均真实波幅(10日)，衡量价格波动性的指标
    - mkt_style: 市场风格分类结果
    - volume: 成交量(单位:手，1手=100股)，反映市场活跃度，高成交量通常伴随价格趋势确认
    """
    # 获取数据
    df = get_stock_hist_data(stock_code=stock_code, end_date=base_date, duration=90+return_days)
    
    if df is not None:
        # 计算技术指标
        df = calculate_rsi(df)
        df = calculate_bollinger_bands(df)
        df = calculate_moving_averages(df)
        df['atr'] = calculate_atr(df)
        
        # 如果需要进行市场风格分类
        if with_market_style:
            df = pd.concat([df, classify_market_style(df)], axis=1)
        df.index.name = 'date'
        # 返回最后return_days条数据
        if return_format == 'markdown':
            return df.tail(return_days).to_markdown()
        else:
            return df.tail(return_days).to_dict(orient='records')
    else:
        raise Exception(f"无法获取数据，请检查输入参数{stock_code}是否正确。")

@mcp.tool(name="screen_etf_anomaly_in_tech", description="筛选ETF异动行情")
def screen_etf_anomaly_in_tech(etf_codes=("513050"), base_date: str = None,
                                    lookback_days: int = 60, top_k: int=10):
    # 处理日期参数
    end_date = datetime.strptime(base_date, '%Y%m%d') if base_date and len(base_date)>=8  else datetime.now()
    
    # 处理ETF代码参数
    etf_list = tuple(etf_codes.split(',')) if etf_codes else None
    return screen_etf_anomaly_cached(etf_list, end_date=end_date,  lookback_days=lookback_days)[0:top_k].to_markdown()



def main():
    #print("欢迎使用ETF技术指标分析工具！")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
