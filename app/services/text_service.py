from __future__ import annotations

import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, Tuple

from app.core.exceptions import ParameterException
from app.models.chat_msg import ChatMsg
from app.utils.enums import ListRiskTypeEnum
from app.utils.language_classification import LanguageClassification
from app.utils.match_data_utils import all_filter

from .validators import TEXT_REQUIRED_FIELDS, ensure_required_fields


def build_base_response(ctx) -> Dict[str, Any]:
    return {
        "status": 0,
        "code": 1100,
        "extra": {
            "server_area": ctx.config.get("COUNTRY"),
            "language": {
                "switch": "ON" if ctx.config.get("LANGUAGE_SWITCH") else "OFF",
                "predict": {},
                "msg": "success",
            },
            "client_ip": "",
            "response_time": {"total": 0},
        },
        "riskLevel": "",
        "detail": {},
        "score": 0,
        "requestId": "",
        "message": "成功",
    }


def build_pass_detail(chat_msg: ChatMsg) -> Dict[str, Any]:
    return {
        "contextProcessed": False,
        "contextText": chat_msg.text,
        "filteredText": "",
        "riskType": ListRiskTypeEnum.NORMAL.value,
        "matchedItem": "",
        "matchedList": "",
        "description": ListRiskTypeEnum.desc(ListRiskTypeEnum.NORMAL.value),
        "descriptionV2": ListRiskTypeEnum.desc(ListRiskTypeEnum.NORMAL.value),
        "matchedDetail": json.dumps({}, ensure_ascii=False),
    }


def process_msg_data(raw_data: Dict[str, Any], ctx) -> Dict[str, Any]:
    if str(raw_data.get("app_id")) == "94" and "channel" not in raw_data:
        raw_data["channel"] = ""
    raw_data.setdefault("relationship", "")
    raw_data.setdefault("target_id", "")
    raw_data.setdefault("request_id", str(uuid.uuid1()))
    raw_data.setdefault("bt_id", str(uuid.uuid1()))

    if raw_data.get("account_id") is None:
        raw_data["token_id"] = f"{raw_data.get('app_id')}_{raw_data.get('server_id')}_{raw_data.get('role_id')}"
    else:
        raw_data["token_id"] = str(raw_data.get("account_id"))

    raw_data["channel"] = f"{raw_data.get('app_id')}_{raw_data.get('channel', '')}"
    raw_data = get_history_chat(raw_data, ctx)
    return raw_data


def get_history_chat(raw_data: Dict[str, Any], ctx) -> Dict[str, Any]:
    if (
        str(raw_data.get("app_id")) not in ["2013101", "2013001"]
        or "NICKNAME_CHECK" in str(raw_data.get("channel"))
        or raw_data.get("text") == ""
    ):
        return raw_data
    redis_client = ctx.config.get("CHAT_LOG_REDIS_CLIENT")
    if not redis_client:
        return raw_data
    try:
        key = f"roleChatContent:{raw_data.get('app_id')}:{raw_data.get('account_id')}:{raw_data.get('role_id')}"
        res = redis_client.get(key)
        if res:
            data = json.loads(res)
            chat_content = data.get("chat_content", {}).get("PRIVATE") or data.get("chat_content", {}).get("私聊频道")
            role_level = data.get("role_level", 0)
            if chat_content and role_level <= 40:
                current_timestamp = int(datetime.now().timestamp())
                one_hour_ago = current_timestamp - 3600
                filtered = [item for item in chat_content if item["timeline"] >= one_hour_ago]
                filtered = sorted(filtered, key=lambda x: x["timeline"])
                raw_data["chat_history"] = [item["chat_content"] for item in filtered]
    except Exception as err:
        ctx.logger.debug(f"获取上下文出错: {err}")
    return raw_data


def handle_text_filter(raw_data: Dict[str, Any], ctx) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    start_time = time.time()
    r = build_base_response(ctx)

    raw_data.setdefault("token_id", None)
    if raw_data.get("app_id") and raw_data.get("token_id") is None:
        raw_data["token_id"] = f"{raw_data.get('app_id')}_{raw_data.get('server_id')}_{raw_data.get('role_id')}"

    ensure_required_fields(raw_data, TEXT_REQUIRED_FIELDS)
    data_params = process_msg_data(raw_data, ctx)

    chat_msg = ChatMsg()
    chat_msg.set_attrs(data_params)

    # app_id 校验
    all_apps = ctx.config.get("ALL_APPS", [])
    if str(chat_msg.app_id) not in all_apps or chat_msg.app_id == "all":
        raise ParameterException(msg="app_id 不存在")

    # 语种识别
    if ctx.config.get("LANGUAGE_SWITCH"):
        language_pred = LanguageClassification.predict(chat_msg, ctx)
        if language_pred:
            language_pred = language_pred.get("language", language_pred)
            r["extra"]["language"]["predict"] = language_pred
        else:
            language_pred = {"nickname": "zh", "text": "zh"}
            r["extra"]["language"]["msg"] = "language predict api timeout!"
    else:
        language_pred = {"nickname": "zh", "text": "zh"}
        r["extra"]["language"]["msg"] = "language switch is OFF"

    # 自研匹配算法过滤
    ml_res = all_filter(chat_msg, r, ctx, language_pred)
    ctx.logger.debug(f"自研匹配算法过滤: {ml_res}")

    if ml_res.get("riskLevel"):
        detail = ml_res.get("detail", {})
        ml_res["detail"] = json.dumps(detail, ensure_ascii=False)
        if not ml_res.get("requestId"):
            ml_res["requestId"] = chat_msg.request_id
        ml_res["extra"]["response_time"]["total"] = int((time.time() - start_time) * 1000)
        return ml_res, data_params

    # 默认 PASS
    r["riskLevel"] = "PASS"
    r["detail"] = json.dumps(build_pass_detail(chat_msg), ensure_ascii=False)
    r["requestId"] = chat_msg.request_id
    r["extra"]["response_time"]["total"] = int((time.time() - start_time) * 1000)
    return r, data_params
