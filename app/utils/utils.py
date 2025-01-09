import pandas as pd
from pathlib import Path
from joblib import dump, load
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
import numpy as np
from sklearn.preprocessing import OrdinalEncoder, MinMaxScaler
# 自定义
from loguru import logger
from data.xt_data_download import download_history_data

def rbf(x, centers, width):
    """径向基函数计算"""
    return np.exp(-((x[:, None] - centers[None, :]) ** 2) / (2 * width ** 2))

def rbf_encode_time_features(dates, num_centers=10):
    """
    使用径向基函数对 day、weekday、month、week 进行编码。

    参数：
    dates (pd.Series): 日期序列。
    num_centers (int): RBF 中心数量。

    返回：
    pd.DataFrame: 编码后的特征矩阵。
    """
    # 提取时间特征
    days = dates.day
    weekdays = dates.weekday  # Monday=0, Sunday=6
    months = dates.month
    weeks = dates.isocalendar().week

    # 归一化时间特征到[0, 1]区间
    scaler = MinMaxScaler()
    days_scaled = scaler.fit_transform(days.values.reshape(-1, 1)).flatten()
    weekdays_scaled = scaler.fit_transform(weekdays.values.reshape(-1, 1)).flatten()
    months_scaled = scaler.fit_transform(months.values.reshape(-1, 1)).flatten()
    weeks_scaled = scaler.fit_transform(weeks.values.reshape(-1, 1)).flatten()

    # 为每个特征创建 RBF 中心和宽度
    day_centers = np.linspace(0, 1, num_centers)
    weekday_centers = np.linspace(0, 1, num_centers)
    month_centers = np.linspace(0, 1, num_centers)
    week_centers = np.linspace(0, 1, num_centers)

    width = 1.0 / num_centers

    # 计算 RBF 编码
    day_rbf = rbf(days_scaled, day_centers, width)
    weekday_rbf = rbf(weekdays_scaled, weekday_centers, width)
    month_rbf = rbf(months_scaled, month_centers, width)
    week_rbf = rbf(weeks_scaled, week_centers, width)

    # 组合成特征矩阵
    encoded_features = np.hstack([day_rbf, weekday_rbf, month_rbf, week_rbf])

    return pd.DataFrame(encoded_features)
