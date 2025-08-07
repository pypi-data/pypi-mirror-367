import flask
import time

import logger_py.logger as logger
import metrics_py.metrics as metrics
from metrics_py.middleware.base import BaseMiddleware

class FlaskMiddleware(BaseMiddleware):
    def __init__(self, app: flask.Flask):
        super().__init__()
        self.app = app

        self.app.before_request(self.before_request)
        self.app.after_request(self.after_request)
        pass
    
    def before_request(self):
        flask.g.start_time = time.time()

    def after_request(self, response: flask.Response):
        try:
            labels = {
                "method": flask.request.path,
                "status": response.status_code
            }       

            metrics.report(
                metric_name=self.LatencyMetric,
                value=(time.time() - flask.g.start_time) * 1000,  # 毫秒
                labels=labels,
            )
            
            metrics.report(
                metric_name=self.ReqCntMetric,
                value=1,
                labels=labels,
            )
            return response
        except Exception as e:
            logger.Warn({}, msg=f"report metric error {e}")
            return response
