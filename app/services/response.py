from __future__ import annotations

import uuid
from typing import Any, Dict, Optional


def new_request_id() -> str:
    return str(uuid.uuid1())


def success_response(msg: str = "成功", data: Optional[Any] = None) -> Dict[str, Any]:
    payload = {"message": msg, "code": 0, "requestId": new_request_id()}
    if data is not None:
        payload["data"] = data
    return payload
