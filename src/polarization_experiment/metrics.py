import math
from collections import defaultdict
from typing import Iterable


def bipolarization_index(values: Iterable[int]) -> float:
    data = list(values)
    if not data:
        raise ValueError("빈 표본의 양극화 지수는 정의되지 않습니다.")
    if any(value < 1 or value > 7 for value in data):
        raise ValueError("척도는 1~7이어야 합니다.")
    n = len(data)
    low = sum(value <= 2 for value in data) / n
    high = sum(value >= 6 for value in data) / n
    middle = 1 - low - high
    return 4 * low * high * (1 - middle)


def gini(values: Iterable[float], weights: Iterable[float] | None = None) -> float:
    x = list(values)
    w = list(weights) if weights is not None else [1.0] * len(x)
    if not x or len(x) != len(w) or any(v < 0 for v in x) or any(v <= 0 for v in w):
        raise ValueError("Gini는 동일 길이의 비음수 값과 양수 가중치가 필요합니다.")
    if sum(v * wt for v, wt in zip(x, w)) == 0:
        return 0.0
    pairs = sorted(zip(x, w))
    total_w = sum(w)
    total_xw = sum(v * wt for v, wt in pairs)
    cumulative_w = cumulative_xw = area = 0.0
    for value, weight in pairs:
        next_w = cumulative_w + weight
        next_xw = cumulative_xw + value * weight
        area += (cumulative_xw + next_xw) * (next_w - cumulative_w)
        cumulative_w, cumulative_xw = next_w, next_xw
    return 1 - area / (total_w * total_xw)


def theil_t(values: Iterable[float]) -> float:
    x = list(values)
    if not x or any(value <= 0 for value in x):
        raise ValueError("Theil T는 양수 값만 허용합니다.")
    mean = sum(x) / len(x)
    return sum((value / mean) * math.log(value / mean) for value in x) / len(x)


def wolfson_polarization(values: Iterable[float]) -> float:
    """Wolfson의 중간층 중심 양극화 지수(비가중 표본)를 계산한다."""
    x = sorted(values)
    if not x or any(value <= 0 for value in x):
        raise ValueError("Wolfson 지수는 양수 값만 허용합니다.")
    n = len(x)
    halfway = n / 2
    whole = int(halfway)
    fraction = halfway - whole
    lower_income = sum(x[:whole])
    if fraction and whole < n:
        lower_income += fraction * x[whole]
    lower_share = lower_income / sum(x)
    median = (x[(n - 1) // 2] + x[n // 2]) / 2
    mean = sum(x) / n
    value = 2 * (2 * (0.5 - lower_share) - gini(x)) * mean / median
    return max(0.0, value)


def theil_between_share(values: Iterable[float], groups: Iterable[str]) -> float | None:
    """Theil T 중 집단 평균 차이로 설명되는 몫을 반환한다."""
    x, g = list(values), list(groups)
    if not x or len(x) != len(g) or any(value <= 0 for value in x):
        raise ValueError("양수 값과 동일 길이의 그룹이 필요합니다.")
    total = theil_t(x)
    if total == 0:
        return None
    grand = sum(x) / len(x)
    buckets: dict[str, list[float]] = defaultdict(list)
    for value, group in zip(x, g):
        buckets[group].append(value)
    between = 0.0
    for bucket in buckets.values():
        group_mean = sum(bucket) / len(bucket)
        ratio = group_mean / grand
        between += (len(bucket) / len(x)) * ratio * math.log(ratio)
    return between / total


def between_group_variance_share(values: Iterable[float], groups: Iterable[str]) -> float | None:
    x, g = list(values), list(groups)
    if not x or len(x) != len(g):
        raise ValueError("값과 그룹 길이가 같아야 합니다.")
    grand = sum(x) / len(x)
    total = sum((value - grand) ** 2 for value in x)
    if total == 0:
        return None
    buckets: dict[str, list[float]] = defaultdict(list)
    for value, group in zip(x, g):
        buckets[group].append(value)
    between = sum(len(group) * ((sum(group) / len(group)) - grand) ** 2 for group in buckets.values())
    return between / total
