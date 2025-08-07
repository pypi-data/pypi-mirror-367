from metrics_py.config import metric_config
from metrics_py.reporter.abstract import Reporter

from logger_py import logger
from prometheus_client import CollectorRegistry, start_http_server


class CollectorReporter(Reporter):
    def __init__(self, metrics_registry: CollectorRegistry, config: metric_config.Config):
        super().__init__(metrics_registry, config)
        pass

    def init(self):
        start_http_server(self.config.port)
        logger.Info(ctx={}, msg=f"CollectorReporter started on port {self.config.port}")
        pass

    def close(self):
        pass
