from prometheus_client import CollectorRegistry
from metrics_py.config import metric_config

class Reporter(object):
    def __init__(self, metrics_registry: CollectorRegistry, config: metric_config.Config):
        self.config: metric_config.Config = config
        self.metrics_registry: CollectorRegistry = metrics_registry
        self.init()

    def __del__(self):
        self.close()


    def init(self):
        raise NotImplementedError("init is not implemented")

    def close(self):
        raise NotImplementedError("close is not implemented")
