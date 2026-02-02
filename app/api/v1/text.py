from fastapi import APIRouter, Depends, Request

from yuyan.app.api.deps import get_ctx
from yuyan.app.core.exceptions import ParameterException
from yuyan.app.utils.kafka_utils import submit_kafka
from yuyan.app.services.text_service import handle_text_filter
from yuyan.app.services.validators import (
    parse_json_string,
    parse_request_payload,
    validate_access_key,
)

router = APIRouter()


@router.api_route("/chatmsg.anti", methods=["GET", "POST"])
async def text_filter(request: Request, ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    access_key = payload.get("accessKey")
    ugc_source = payload.get("ugcSource")
    if not ugc_source:
        raise ParameterException(msg="参数不合法(ugcSource not exist)")

    raw_data = payload.get("data")
    if raw_data is None:
        raise ParameterException(msg="参数不合法(data is empty)")
    if isinstance(raw_data, str):
        raw_data = parse_json_string(raw_data)

    validate_access_key(access_key, raw_data.get("gameId"), ctx)
    response, data_params = handle_text_filter(raw_data, ctx)

    request_ip = request.headers.get("Yz-Client-Ip")
    if request_ip:
        request_ip = request_ip.split(",")[0]
    else:
        request_ip = request.client.host if request.client else ""
    response["extra"]["client_ip"] = request_ip

    try:
        submit_kafka(data_params, response, ctx)
    except Exception as err:
        ctx.logger.debug(f"submit kafka error: {err}")

    return response
