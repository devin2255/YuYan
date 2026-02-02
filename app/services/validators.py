from __future__ import annotations

import json
from typing import Any, Dict

from yuyan.app.core.exceptions import ParameterException



TEXT_REQUIRED_FIELDS = [
    "timestamp",
    "tokenId",
    "nickname",
    "text",
    "serverId",
    "accountId",
    "gameId",
    "roleId",
    "vipLevel",
    "level",
    "ip",
    "channel",
]

IMAGE_REQUIRED_FIELDS = [
    "timestamp",
    "img",
    "serverId",
    "accountId",
    "gameId",
    "roleId",
    "vipLevel",
    "level",
    "ip",
    "channel",
    "targetId",
    "organizationId",
    "teamId",
    "sceneId",
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


def validate_access_key(access_key: str, game_id: str, ctx) -> None:
    if not access_key or not str(access_key).strip():
        raise ParameterException(msg="参数不合法(accessKey not exist)")
    cache_map = ctx.config.get("ACCESS_KEY", {})
    fallback_map = ctx.config.get("ACCESS_KEY_FALLBACK", {})
    if fallback_map.get(access_key) is None and cache_map.get(str(game_id), "") != access_key:
        raise ParameterException(msg="参数不合法(accessKey not exist)")


async def parse_request_payload(request) -> Dict[str, Any]:
    data = {}
    try:
        data = await request.json()
    except Exception:
        data = {}
    if data:
        return data

    try:
        form = await request.form()
        if form:
            for key, value in form.multi_items():
                if key in data:
                    if not isinstance(data[key], list):
                        data[key] = [data[key]]
                    data[key].append(value)
                else:
                    data[key] = value
            return data
    except Exception:
        pass

    for key, value in request.query_params.multi_items():
        if key in data:
            if not isinstance(data[key], list):
                data[key] = [data[key]]
            data[key].append(value)
        else:
            data[key] = value
    return data
