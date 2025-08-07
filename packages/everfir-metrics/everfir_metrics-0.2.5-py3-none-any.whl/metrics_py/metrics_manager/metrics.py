from typing import Dict
import logger_py.logger as logger
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, Summary

from metrics_py.config import metric_config
from metrics_py.reporter import NewReporter
import metrics_py.reporter.abstract as abstract
from metrics_py.util.env import get_container_ip, get_env
from metrics_py.metrics_manager.metric_info import MetricName, MetricType, MetricInfo


__all__ = [
    "MetricsManager",
]


class MetricsManager:
    def __init__(self, config: metric_config.Config):
        self.config: metric_config.Config = config

        # 内置标签
        self.build_in_labels: Dict[str, str] = {
            "env": get_env(),
            "container_ip": get_container_ip(),
        }

        self.metrics_registry: CollectorRegistry = CollectorRegistry()
        self.reporter: abstract.Reporter = NewReporter(
            self.metrics_registry, self.config
        )

        # 已经注册的指标
        self.metrics_info: Dict[MetricName, MetricInfo] = {}
        self.gauges: Dict[MetricName, Gauge] = {}
        self.counters: Dict[MetricName, Counter] = {}
        self.histograms: Dict[MetricName, Histogram] = {}
        self.summaries: Dict[MetricName, Summary] = {}
        pass

    def register(self, metric_info: MetricInfo) -> None:
        metric_info.labels.extend(self.build_in_labels.keys())
        return register_metric(self, metric_info)

    def report(self, metric_name: MetricName, value: float, labels: dict) -> None:
        labels.update(self.build_in_labels)
        return report_metric(self, metric_name, value, labels)


def register_metric(metrics_manager: "MetricsManager", metric_info: MetricInfo) -> None:
    if metric_info.metric_type == MetricType.GAUGE:
        metric = register_gauge(metrics_manager, metric_info)
        metrics_manager.gauges[metric_info.name] = metric
    elif metric_info.metric_type == MetricType.COUNTER:
        metric = register_counter(metrics_manager, metric_info)
        metrics_manager.counters[metric_info.name] = metric
    elif metric_info.metric_type == MetricType.HISTOGRAM:
        metric = register_histogram(metrics_manager, metric_info)
        metrics_manager.histograms[metric_info.name] = metric
    elif metric_info.metric_type == MetricType.SUMMARY:
        metric = register_summary(metrics_manager, metric_info)
        metrics_manager.summaries[metric_info.name] = metric
    else:
        raise ValueError(f"Invalid metric type: {metric_info.metric_type}")

    metrics_manager.metrics_info[metric_info.name] = metric_info
    logger.Debug(ctx={}, msg=f"register metric {metric_info.name}")
    pass


def register_gauge(metrics_manager: MetricsManager, metric_info: MetricInfo) -> Gauge:
    gauge = Gauge(
        namespace=metrics_manager.config.namespace,
        subsystem=metrics_manager.config.service_name,
        name=metric_info.name,
        documentation=metric_info.help,
        labelnames=metric_info.labels,
    )
    return gauge


def register_counter(
    metrics_manager: MetricsManager, metric_info: MetricInfo
) -> Counter:
    counter = Counter(
        namespace=metrics_manager.config.namespace,
        subsystem=metrics_manager.config.service_name,
        name=metric_info.name,
        documentation=metric_info.help,
        labelnames=metric_info.labels,
    )
    return counter


def register_histogram(
    metrics_manager: MetricsManager, metric_info: MetricInfo
) -> Histogram:
    histogram = Histogram(
        namespace=metrics_manager.config.namespace,
        subsystem=metrics_manager.config.service_name,
        name=metric_info.name,
        documentation=metric_info.help,
        labelnames=metric_info.labels,
        buckets=metric_info.buckets,
    )
    return histogram


def register_summary(
    metrics_manager: MetricsManager, metric_info: MetricInfo
) -> Summary:
    summary = Summary(
        namespace=metrics_manager.config.namespace,
        subsystem=metrics_manager.config.service_name,
        name=metric_info.name,
        documentation=metric_info.help,
        labelnames=metric_info.labels,
    )
    return summary


def report_metric(
    metrics_manager: MetricsManager,
    metric_name: MetricName,
    value: float,
    label: dict,
) -> None:
    if not metrics_manager.metrics_info[metric_name]:
        return

    metrics_type: MetricType = metrics_manager.metrics_info[metric_name].metric_type
    if metrics_type == MetricType.GAUGE:
        return report_gauge(metrics_manager, metric_name, value, label)
    elif metrics_type == MetricType.COUNTER:
        return report_counter(metrics_manager, metric_name, value, label)
    elif metrics_type == MetricType.HISTOGRAM:
        return report_histogram(metrics_manager, metric_name, value, label)
    elif metrics_type == MetricType.SUMMARY:
        return report_summary(metrics_manager, metric_name, value, label)


def report_gauge(
    metrics_manager: MetricsManager,
    metric_name: MetricName,
    value: float,
    labels: dict,
) -> None:
    metric = metrics_manager.gauges.get(metric_name)
    if metric:
        metric.labels(**labels).set(value)
    else:
        raise ValueError(f"Metric {metric_name} not found")


def report_counter(
    metrics_manager: MetricsManager,
    metric_name: MetricName,
    value: float,
    labels: dict,
) -> None:
    metric = metrics_manager.counters.get(metric_name)
    if metric:
        metric.labels(**labels).inc(value)
    else:
        raise ValueError(f"Metric {metric_name} not found")


def report_histogram(
    metrics_manager: MetricsManager,
    metric_name: MetricName,
    value: float,
    labels: dict,
) -> None:
    metric = metrics_manager.histograms.get(metric_name)
    if metric:
        metric.labels(**labels).observe(value)
    else:
        raise ValueError(f"Metric {metric_name} not found")


def report_summary(
    metrics_manager: MetricsManager,
    metric_name: MetricName,
    value: float,
    labels: dict,
) -> None:
    metric = metrics_manager.summaries.get(metric_name)
    if metric:
        metric.labels(**labels).observe(value)
    else:
        raise ValueError(f"Metric {metric_name} not found")
