import os
from typing import Optional

ReportType = int
RT_COLLECTOR = 1
RT_PUSHGATEWAY = 2


class Config:
    def __init__(self):
        self.namespace:str = os.getenv("NAMESPACE", "") # 指标命名空间
        self.service_name:str = os.getenv("SERVICE_NAME", "") # 服务名

        self.report_type: ReportType = RT_COLLECTOR  # 默认由旁路collector采集
        self.port:int = int(os.getenv("METRICS_PORT", 10083))# 服务端口, 仅在collecotr模式下有效
        self.job_name:str = self.service_name       # PushGateway的job名, 仅在PushGateway模式下有效
        self.push_interval_sec:int = 15   # PushGateway的push间隔, 仅在PushGateway模式下有效, 单位为秒
        self.push_gateway_url:str = os.getenv("METRICS_PUSH_GATEWAY_URL", "") # PushGateway地址, 仅在PushGateway模式下有效
        pass

    def validate(self) -> Optional[Exception]:
        err: Optional[Exception] = None

        if err := _validate_namespace(self):
            return err

        if err := _validate_service_name(self):
            return err

        if err := _validate_report_type(self):
            return err

        return None


def _validate_namespace(config: Config) -> Optional[Exception]:
    if config.namespace == "":
        return Exception("namespace is empty")
    return None

def _validate_service_name(config: Config) -> Optional[Exception]:
    if config.service_name == "":
        return Exception("service_name is empty")
    return None

def _validate_report_type(config: Config) -> Optional[Exception]:
    if config.report_type == RT_COLLECTOR:
        if config.port == 0:
            return Exception("port is 0 in collector mode")
        elif config.report_type == RT_PUSHGATEWAY:
            if config.push_gateway_url == "":
                return Exception("push_gateway_url is empty in pushgateway mode")
            if config.job_name == "":
                return Exception("job_name is empty in pushgateway mode")
        else:
            return Exception("invalid report type")

    return None



_global_config: Config = Config()

def GetConfig() -> Config:
    return _global_config