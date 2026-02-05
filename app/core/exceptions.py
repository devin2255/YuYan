from __future__ import annotations

import uuid
from typing import Any, Optional


class APIException(Exception):
    status_code = 500
    error_code = 999
    message = "服务器未知错误"

    def __init__(
        self,
        message: Optional[str] = None,
        *,
        msg: Optional[str] = None,
        status_code: Optional[int] = None,
        error_code: Optional[int] = None,
        data: Optional[Any] = None,
        request_id: Optional[str] = None,
    ):
        if message is None and msg is not None:
            message = msg
        super().__init__(message or self.message)
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        if message is not None:
            self.message = message
        self.data = data
        self.request_id = request_id or str(uuid.uuid4())


class ServerError(APIException):
    status_code = 500
    error_code = 999
    message = "服务器未知错误"


class ParameterException(APIException):
    status_code = 200
    error_code = 1902
    message = "参数错误"


class NotFound(APIException):
    status_code = 404
    error_code = 10020
    message = "资源不存在"


class Unauthorized(APIException):
    status_code = 401
    error_code = 40100
    message = "未授权"
