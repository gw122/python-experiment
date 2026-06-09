# 数据清洗模块 wash.py 说明
#
# 数据清洗初始化：     data = DataWasher(read_csv(...))
# 获取DataFrame：    result = data.as_raw()
# 应用默认清洗规则：   data.replace(data.iter().filter(rule_drop_invalid).collect())
#
# 自定义清洗规则
# 筛选 2.0~5.0 的风力：result = data.iter().filter(lambda x: rule_minmax(x, 'wind', 2.0, 5.0)).collect()
# 筛选雨天：           result = data.iter().filter(lambda x: rule_eq(x, 'weather', 'rain')).collect()
# 保留整数：           result = data.iter().map(_diyrule_round).collect()

from time import strptime
from typing import Callable, Self
from pandas import DataFrame, Series
import numpy
from numpy import float64 as f64
from numpy import isnan

# 逐行处理数据的迭代器，数据类型为 pandas.Series
# 调用 filter 或者 map 自定义数据清洗规则
# 调用 collect 将清洗后的数据收集到新的 pandas.DataFrame 中
# 支持链式调用
class DataIterator:
    def __init__(self, inner: DataFrame):
        self._inner: DataFrame = inner
        self._index: int = 0
        self._closures: list[Callable] = list()

# 函数 filter：过滤数据
# 参数 f：函数或者lambda表达式，接收一行数据，返回True保留该行，返回False丢弃该行
    def filter(self, f: Callable[[Series], bool]) -> Self:
        self._closures.append(f)
        return self

# 函数 map：改变数据
# 参数 f：函数或者lambda表达式，接收一行数据，处理之后返回新的数据。如果不想改变数据，直接返回参数即可。
    def map(self, f: Callable[[Series], Series]) -> Self:
        self._closures.append(f)
        return self

    def next(self) -> Series | None:
        while self._index < len(self._inner):
            this = self._inner.loc[self._index]
            skip = False
            for closure in self._closures:
                result = closure(this)
                if type(result) == bool or type(result) == numpy.bool:
                    if not result:
                        skip = True
                        break
                elif type(result) == Series:
                    this = result
                else:
                    raise ValueError(type(result))
            self._index += 1
            if not skip:
                return this
        return None

    def collect(self) -> DataFrame:
        items = list()
        this = self.next()
        cnt = 0
        while this is not None:
            this.name = cnt
            items.append(this)
            this = self.next()
            cnt += 1
        return DataFrame(items, columns=self._inner.columns, copy=True)

# 数据清洗模块
class DataWasher:
    def __init__(self, rawdata: DataFrame):
        self._inner: DataFrame = rawdata

    def as_raw(self, clone: bool = False) -> DataFrame:
        return self._inner.copy(deep=True) if clone else self._inner

    def iter(self) -> DataIterator:
        return DataIterator(self.as_raw())

    def replace(self, newdata: DataFrame):
        self._inner = newdata

# 默认规则：剔除错误数据
def rule_drop_invalid(x: Series) -> bool:
    try:
        strptime(x['date'], "%Y-%m-%d")
        return isinstance(x['precipitation'], f64) and isinstance(x['temp_max'], f64) and isinstance(x['temp_min'], f64) and isinstance(x['wind'], f64) and isinstance(x['weather'], str) and (not isnan(x['precipitation'])) and (not isnan(x['temp_max'])) and (not isnan(x['temp_min'])) and (not isnan(x['wind'])) and x['temp_max'] >= x['temp_min'] and x['precipitation'] >= 0.0 and x['wind'] >= 0.0 and (x['weather'] in ['drizzle', 'rain', 'sun', 'snow', 'fog'])
    except:
        return False

# 自定义规则：筛选区间之内的数据
def rule_minmax(x: Series, _col: str, _min, _max):
    try:
        return _min <= x[_col] <= _max
    except:
        return False

# 自定义规则：筛选指定的数据
def rule_eq(x: Series, _col: str, _val):
    try:
        return x[_col] == _val
    except:
        return False

# 调试
# 自定义规则：保留整数
def _diyrule_round(x: Series) -> Series:
    for it in ['precipitation', 'temp_max', 'temp_min', 'wind']:
        x[it] = int(round(x[it], 0))
    return x

if __name__ == '__main__':
    from pandas import read_csv
    data = DataWasher(read_csv("seattle-weather.csv", sep=','))
    data.replace(data.iter().filter(rule_drop_invalid).collect())
    it = data.iter()
    it.filter(lambda x: rule_minmax(x, 'wind', 2.0, 5.0))
    it.filter(lambda x: rule_eq(x, 'weather', 'rain'))
    it.map(_diyrule_round)
    print(it.collect())
    print(data.as_raw())