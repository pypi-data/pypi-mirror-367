
from metrics_py.metrics import register
from metrics_py.metrics_manager.metrics import MetricName
from metrics_py.metrics_manager.metric_info import MetricInfo, MT_COUNTER, MT_HISTOGRAM



class BaseMiddleware(object):
    def __init__(self):
        print("hyb_debug: init middleware")
        self.ReqCntMetric: MetricName = "req_cnt"
        self.LatencyMetric: MetricName = "latency"

        register(MetricInfo(
            metric_type=MT_COUNTER,
            name=self.ReqCntMetric,
            help="request count",
            labels=["method", "status"]
        ))
        register(MetricInfo(
            metric_type=MT_HISTOGRAM,
            name=self.LatencyMetric,
            help="request latency",
            labels=["method", "status"]
        ))
        pass