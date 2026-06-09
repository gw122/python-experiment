# main.py

import pandas as pd
from modules.data_cleaner import (
    DataWasher,
    rule_drop_invalid,
    rule_minmax,
    rule_eq,
    _diyrule_round
)

from modules.visualization import plot_weather_animation
from modules.data_manager import app


def test_cleaner():
    """
    测试数据清洗模块
    """

    print("========== 数据清洗测试 ==========")

    df = pd.read_csv("data/seattle-weather.csv")

    print("原始数据条数：", len(df))

    washer = DataWasher(df)

    # 默认规则清洗
    washer.replace(
        washer.iter()
        .filter(rule_drop_invalid)
        .collect()
    )

    print("清洗后数据条数：", len(washer.as_raw()))

    # 示例：筛选风速2~5之间且天气为雨天
    result = (
        washer.iter()
        .filter(lambda x: rule_minmax(x, "wind", 2.0, 5.0))
        .filter(lambda x: rule_eq(x, "weather", "rain"))
        .map(_diyrule_round)
        .collect()
    )

    print("\n筛选结果前5行：")
    print(result.head())

    return washer.as_raw()


def test_visualization(df):
    """
    测试可视化模块
    """

    print("\n========== 数据可视化测试 ==========")
    print("关闭图形窗口后继续执行")

    plot_weather_animation(df)


def run_web_system():
    """
    启动Flask系统
    """

    print("\n========== 启动数据管理系统 ==========")
    print("浏览器访问:")
    print("http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )


if __name__ == "__main__":

    clean_df = test_cleaner()

    test_visualization(clean_df)

    input("测试完成，按回车启动Web系统...")

    app.run(
        debug=True,
        use_reloader=False
    )
