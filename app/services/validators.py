from __future__ import annotations

import json
from typing import Any, Dict

from app.core.exceptions import ParameterException



TEXT_REQUIRED_FIELDS = [
    "timestamp",
    "token_id",
    "nickname",
    "text",
    "server_id",
    "account_id",
    "app_id",
    "role_id",
    "vip_level",
    "level",
    "ip",
    "channel",
]

IMAGE_REQUIRED_FIELDS = [
    "timestamp",
    "img",
    "server_id",
    "account_id",
    "app_id",
    "role_id",
    "vip_level",
    "level",
    "ip",
    "channel",
    "target_id",
    "organization_id",
    "team_id",
    "scene_id",
]



class Field:
    def __init__(self, data: Any):
        self.data = data


class FormProxy:
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(self, key, Field(value))


def parse_json_string(raw: str) -> Dict[str, Any]:
    if not raw or raw == "{}":
        raise ParameterException(msg="参数不合法(data is empty)")
    try:
        return json.loads(raw, strict=False)
    except Exception:
        cleaned = (
            raw.replace("\n", "")
            .replace("\xa0", "")
            .replace("\t", "")
            .replace("\\", "")
            .replace("\n\n", "")
            .replace("\r", "")
        )
        return json.loads(cleaned, strict=False)


def ensure_required_fields(raw_data: Dict[str, Any], required_fields) -> None:
    missing = [k for k in required_fields if k not in raw_data]
    if missing:
        raise ParameterException(msg=f"参数不合法(data key {missing[0]} not exist)")


def validate_access_key(access_key: str, app_id: str, ctx) -> None:
    if not access_key or not str(access_key).strip():
        raise ParameterException(msg="参数不合法(access_key not exist)")
    cache_map = ctx.config.get("ACCESS_KEY", {})
    fallback_map = ctx.config.get("ACCESS_KEY_FALLBACK", {})
    if fallback_map.get(access_key) is None and cache_map.get(str(app_id), "") != access_key:
        raise ParameterException(msg="参数不合法(access_key not exist)")


