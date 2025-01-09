import csv
from xtquant import xtdata
from datetime import datetime
from pathlib import Path
import time
import math
from typing import List, Optional
# 自定义
from loguru import logger
from app.config import config

def get_targets_list_from_csv():
    """
    从csv文件中读取股票代码列表
    """
    csv_file_path = str((Path(__file__).parent.parent / config.investment_targets).absolute())
    stock_list = []
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['STATUS'] == 'True':
                    stock_list.append(row['SECURE'])
    except Exception as e:
        logger.error(f"Error reading CSV file: {e}")
    return stock_list

def download_history_data(
        stock_list: Optional[List[str]] = None,
        period: str = '1d',
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        callback: Optional[callable] = None,
        incrementally: bool = False
) -> None:
    """
    下载指定股票列表的历史数据。

    :param stock_list: 股票代码列表，默认为从 CSV 文件获取
    :param period: 时间周期，默认 '1d'
    :param start_time: 起始时间，格式为 'YYYYMMDD'，默认 '20160101'
    :param end_time: 结束时间，格式为 'YYYYMMDD%H%M%S'，默认当前日期
    :param callback: 下载数据时的回调函数，默认 None
    :param incrementally: 是否增量下载，默认 False
    """
    if stock_list is None:
        stock_list = get_targets_list_from_csv()
    start_time = start_time or '20160101'
    end_time = end_time or datetime.now().strftime('%Y%m%d%H%M%S')

    for stock in stock_list:
        try:
            xtdata.download_history_data(stock, period, start_time, end_time, incrementally=incrementally)
            logger.info(f"成功下载股票数据：{stock}")
        except Exception as e:
            logger.error(f"下载股票数据失败：{stock}，错误信息：{e}")
