from typing import List




# 线性桶
def linear_buckets(start: float, width: float, count: int) -> List[float]:
    return [start + i * width for i in range(count)]


# 对数桶
def exponential_buckets(start: float, factor: float, count: int) -> List[float]:
    return [start * factor ** i for i in range(count)]

__all__ = ["linear_buckets", "exponential_buckets"]