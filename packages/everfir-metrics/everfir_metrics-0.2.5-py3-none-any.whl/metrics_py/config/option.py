from typing import Callable

from metrics_py.config import metric_config

Option = Callable[[metric_config.Config], None]

def WithNamespace(namespace:str) -> Option:
    def option(config:metric_config.Config):
        config.namespace = namespace
    return option


def WithServiceName(service_name:str) -> Option:
    def option(config:metric_config.Config):
        config.service_name = service_name
    return option

def WithPushGateway(
        push_gateway_url:str, 
        job_name:str, 
        push_interval_sec:int
    ) -> Option:
    def option(config:metric_config.Config):
        config.report_type = metric_config.RT_PUSHGATEWAY
        config.push_gateway_url = push_gateway_url
        config.job_name = job_name
        config.push_interval_sec = push_interval_sec
    return option


def WithCollector(port:int) -> Option:
    def option(config:metric_config.Config):
        config.report_type = metric_config.RT_COLLECTOR
        config.port = port
    return option
