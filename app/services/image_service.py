from __future__ import annotations

import json
import uuid
from typing import Any, Dict, Tuple

from app.utils.enums import ListRiskTypeEnum

from .validators import IMAGE_REQUIRED_FIELDS, ensure_required_fields


def process_image_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    if raw_data.get("token_id") is None:
        raw_data["token_id"] = f"{raw_data.get('app_id')}_{raw_data.get('server_id')}_{raw_data.get('role_id')}"
    raw_data.setdefault("request_id", str(uuid.uuid1()))
    raw_data.setdefault("bt_id", str(uuid.uuid1()))
    return raw_data


def build_pass_detail() -> Dict[str, Any]:
    return {
        "contextProcessed": False,
        "contextText": "",
        "filteredText": "",
        "riskType": ListRiskTypeEnum.NORMAL.value,
        "matchedItem": "",
        "matchedList": "",
        "description": ListRiskTypeEnum.desc(ListRiskTypeEnum.NORMAL.value),
        "descriptionV2": ListRiskTypeEnum.desc(ListRiskTypeEnum.NORMAL.value),
        "matchedDetail": json.dumps({}, ensure_ascii=False),
    }


def handle_image_filter(raw_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    ensure_required_fields(raw_data, IMAGE_REQUIRED_FIELDS)
    data_params = process_image_data(raw_data)
    response = {
        "status": 0,
        "code": 1100,
        "riskLevel": "PASS",
        "detail": json.dumps(build_pass_detail(), ensure_ascii=False),
        "score": 0,
        "requestId": data_params.get("request_id", ""),
        "message": "成功",
        "extra": {},
    }
    return response, data_params
