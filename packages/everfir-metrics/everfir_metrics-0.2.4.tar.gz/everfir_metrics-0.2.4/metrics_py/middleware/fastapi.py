import time
import json
from typing import Callable, List, Optional
import fastapi
from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logger_py.logger as logger

from metrics_py import metrics
from metrics_py.metrics_manager.metric_info import (
    MetricInfo,
    MetricType,
    exponential_buckets,
)


class FastAPIMiddleware(BaseHTTPMiddleware):
    # 默认的指标定义
    DEFAULT_METRICS: List[MetricInfo] = [
        MetricInfo(
            metric_type=MetricType.COUNTER,
            name="requests_counter",
            help="Total number of requests",
            labels=["method", "path", "status", "code", "country"],
        ),
        MetricInfo(
            metric_type=MetricType.HISTOGRAM,
            name="request_duration",
            help="HTTP request duration in milliseconds",
            labels=["method", "path", "status", "code", "country"],
            buckets=exponential_buckets(
                start=50, factor=1.85, count=12  #  [50ms -> 60s]
            ),
        ),
    ]

    def _extract_response_code(self, response_body: bytes) -> Optional[str]:
        """
        从响应体中提取业务状态码
        
        Args:
            response_body: 响应体字节数据
            
        Returns:
            Optional[str]: 提取到的code值，解析失败时返回None
        """
        try:
            # 尝试解析JSON
            response_text = response_body.decode('utf-8')
            response_data = json.loads(response_text)
            
            # 检查响应数据格式
            if isinstance(response_data, dict):
                # 优先检查code字段
                if 'code' in response_data and response_data['code'] is not None:
                    return str(response_data['code'])
                # 其次检查err_code字段
                elif 'err_code' in response_data and response_data['err_code'] is not None:
                    return str(response_data['err_code'])
                # 如果都没有有效值，返回None（不添加code标签）
                
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            # 解析失败时静默处理，不影响正常流程
            pass
            
        return None

    def _is_streaming_response(self, response: any) -> bool:
        """
        判断是否为流式响应
        
        Args:
            response: FastAPI响应对象
            
        Returns:
            bool: 是否为流式响应
        """
        # 检查是否为StreamingResponse类型
        if isinstance(response, StreamingResponse):
            return True
        
        # 检查是否为中间件包装的StreamingResponse类型
        response_class_name = response.__class__.__name__
        if "_StreamingResponse" in response_class_name:
            return True
            
        # 检查是否有body_iterator属性（StreamingResponse的特征）
        if hasattr(response, 'body_iterator') and callable(getattr(response, 'body_iterator', None)):
            return True
            
        return False

    def __init__(self, app: fastapi.FastAPI):
        super().__init__(app)
        for metric in self.DEFAULT_METRICS:
            metrics.register(metric)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """处理请求并收集指标"""
        # 记录开始时间
        start_time = time.time()

        try:
            # 处理请求
            response = await call_next(request)

            # 计算请求处理时间（毫秒）
            duration_ms = (time.time() - start_time) * 1000

            # 获取请求头中的country
            country = request.headers.get("Cf-Ipcountry")

            # 构造标签
            labels = {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "country": country,
            }

            # 对于流式响应，不尝试读取响应体，直接记录指标
            is_streaming = self._is_streaming_response(response)
            logger.Info({}, msg=f"response: {response}", isStreaming=is_streaming, response_type=type(response).__name__)
            if is_streaming:
                # 流式响应不提取业务状态码，避免破坏流式特性
                labels["code"] = "0" 
                metrics.report(
                    metric_name="requests_counter",
                    value=1,
                    labels=labels,
                )
                metrics.report(
                    metric_name="request_duration",
                    value=duration_ms,
                    labels=labels,
                )
                return response
            else:
                # 读取响应体内容
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # 尝试提取业务状态码
                business_code = self._extract_response_code(response_body)
                # 如果成功提取到业务状态码，添加到标签中
                if business_code is not None:
                    labels["code"] = business_code

                # 记录请求计数
                metrics.report(
                    metric_name="requests_counter",
                    value=1,
                    labels=labels,
                )

                # 记录请求延迟
                metrics.report(
                    metric_name="request_duration",
                    value=duration_ms,
                    labels=labels,
                )

                # 重新构造响应对象以确保客户端能正常接收
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=response.headers,
                    media_type=response.media_type,
                )
        except Exception as e:
            logger.Warn({}, msg=f"Error processing request: {e}")
            return Response(
                    content=b"Unknown error",
                    status_code=500,
                    headers={},
                    media_type="",
                )
