# 未测试
import time

import metrics_py.metrics as metrics
from metrics_py.middleware.base import BaseMiddleware

from grpc import ServerInterceptor


class MetricsInterceptor(ServerInterceptor, BaseMiddleware):
    def __init__(self):
        BaseMiddleware.__init__(self)
        ServerInterceptor.__init__(self)
        pass

    def intercept_service(self, continuation, handler_call_details):
        # 记录请求开始时间
        start_time = time.time()
        method_name = handler_call_details.method.split('/')[-1]

        # 继续处理请求
        response = continuation(handler_call_details)

        # 记录请求结束时间
        end_time = time.time()
        status_code = response.code()
        labels = {
            "method": method_name,
            "status": status_code
        }

        metrics.report(self.ReqCntMetric, 1, labels)    
        metrics.report(self.LatencyMetric, end_time - start_time, labels)
        return response