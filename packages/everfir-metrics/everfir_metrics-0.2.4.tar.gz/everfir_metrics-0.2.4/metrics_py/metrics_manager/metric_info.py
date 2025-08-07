from enum import IntEnum
from typing import List

from metrics_py.util.metric import exponential_buckets

__all__ = [
    "MetricInfo",
    "MetricName",
    "MetricType",
    "MT_COUNTER",
    "MT_GAUGE",
    "MT_HISTOGRAM",
    "MT_SUMMARY",
]
__all__.extend("metric_name")


class MetricType(IntEnum):
    COUNTER = 1
    GAUGE = 2
    HISTOGRAM = 3
    SUMMARY = 4


MetricName = str


def metric_name(name: str) -> MetricName:
    return name


class MetricInfo:
    def __init__(
        self,
        metric_type: MetricType,
        name: MetricName,
        help: str = "",
        labels: List[str] = [],  # 自定义标签
        buckets: List[float] = exponential_buckets(
            1, 2, 10
        ),  # 默认对数桶，范围「1-512」
    ):

        self.metric_type: MetricType = metric_type

        self.help: str = help
        self.name: MetricName = name
        self.labels: List[str] = labels
        self.buckets: List[float] = buckets
        pass
