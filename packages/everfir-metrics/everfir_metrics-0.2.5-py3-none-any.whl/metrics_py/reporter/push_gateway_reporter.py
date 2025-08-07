import time
import threading
from typing import Optional

from metrics_py.config import metric_config
from metrics_py.reporter.abstract import Reporter

from prometheus_client import CollectorRegistry, push_to_gateway


# 推送网关报告器，在后台将metrics推送到pushgateway
class PushGatewayReporter(Reporter):
    def __init__(self, metrics_registry: CollectorRegistry, config: metric_config.Config):
        super().__init__(metrics_registry, config)
        self.thread: Optional[threading.Thread] = None

    def init(self):
        self.thread = threading.Thread(target=self._push_metrics_periodically)
        self.thread.daemon = True
        self.thread.start()
        pass

    def close(self):
        if self.thread:
            self.thread.join()
            self.thread = None

    def _push_metrics_periodically(self):
        while True:
            push_to_gateway(self.config.push_gateway_url, job=self.config.job_name, registry=self.metrics_registry)
            time.sleep(super().config.push_interval_sec)
