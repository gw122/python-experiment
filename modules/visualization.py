# modules/visualization.py
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider

def plot_weather_animation(df, init_interval=50):
    """
    动态可视化 Seattle Weather 数据
    - 左上：温度折线图（Max/Min Temp）
    - 右上：降水柱状图
    - 左下：风速直方图
    - 右下：天气饼图
    - 下方滑块可调节动画速度
    """
    df['date'] = pd.to_datetime(df['date'])

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(bottom=0.15)  # 给滑块留空间
    fig.suptitle("Seattle Weather Interactive Visualization", fontsize=16)

    # 温度折线图
    line_max, = axs[0, 0].plot([], [], label='Max Temp', color='r')
    line_min, = axs[0, 0].plot([], [], label='Min Temp', color='b')
    axs[0, 0].set_title("Temperature Trend")
    axs[0, 0].set_xlabel("Date")
    axs[0, 0].set_ylabel("Temperature (°C)")
    axs[0, 0].legend()
    axs[0, 0].grid(True)

    # 降水柱状图
    axs[0, 1].set_title("Precipitation Trend")
    axs[0, 1].set_xlabel("Date")
    axs[0, 1].set_ylabel("Precipitation (mm)")
    axs[0, 1].grid(True)

    # 静态直方图
    axs[1, 0].hist(df['wind'], bins=20, color='green', edgecolor='black')
    axs[1, 0].set_title("Wind Speed Distribution")
    axs[1, 0].set_xlabel("Wind Speed (km/h)")
    axs[1, 0].set_ylabel("Frequency")
    axs[1, 0].grid(True)

    # 静态饼图
    weather_counts = df['weather'].value_counts()
    axs[1, 1].pie(weather_counts, labels=weather_counts.index,
                  autopct='%1.1f%%', startangle=140)
    axs[1, 1].set_title("Weather Type Distribution")

    # 初始化函数
    def init():
        line_max.set_data([], [])
        line_min.set_data([], [])
        return line_max, line_min

    # 更新函数
    def update(frame):
        current = df.iloc[:frame]

        # 更新温度折线
        line_max.set_data(current['date'], current['temp_max'])
        line_min.set_data(current['date'], current['temp_min'])
        axs[0, 0].set_xlim(df['date'].min(), df['date'].max())
        temp_min = df['temp_min'].min() - 2
        temp_max = df['temp_max'].max() + 2
        axs[0, 0].set_ylim(temp_min, temp_max)

        # 更新降水柱状
        axs[0, 1].clear()
        axs[0, 1].bar(current['date'], current['precipitation'], width=2, color='skyblue')
        axs[0, 1].set_title("Precipitation Trend")
        axs[0, 1].set_xlabel("Date")
        axs[0, 1].set_ylabel("Precipitation (mm)")
        axs[0, 1].grid(True)
        axs[0, 1].set_xlim(df['date'].min(), df['date'].max())
        axs[0, 1].set_ylim(0, df['precipitation'].max() + 5)

        return line_max, line_min

    # 创建动画
    ani = FuncAnimation(fig, update, frames=len(df), init_func=init,
                        interval=init_interval, repeat=True)

    # 添加滑块
    ax_slider = plt.axes([0.25, 0.05, 0.5, 0.03])
    slider = Slider(ax_slider, 'Speed', valmin=1, valmax=200, valinit=init_interval)

    def update_speed(val):
        ani.event_source.interval = slider.val

    slider.on_changed(update_speed)

    plt.show()