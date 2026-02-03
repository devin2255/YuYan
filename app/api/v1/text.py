from fastapi import APIRouter, Depends, Request

from app.api.deps import get_ctx
from app.core.exceptions import ParameterException
from app.schemas.text import TextRequest
from app.utils.kafka_utils import submit_kafka
from app.services.text_service import handle_text_filter
from app.services.validators import (
    parse_json_string,
    validate_access_key,
)

router = APIRouter(prefix="/moderation")


@router.post("/text")
async def text_filter(payload: TextRequest, request: Request, ctx=Depends(get_ctx)):
    access_key = payload.access_key
    ugc_source = payload.ugc_source
    if not ugc_source:
        raise ParameterException(msg="参数不合法(ugc_source not exist)")

    raw_data = payload.data
    if raw_data is None:
        raise ParameterException(msg="参数不合法(data is empty)")
    if isinstance(raw_data, str):
        raw_data = parse_json_string(raw_data)

    validate_access_key(access_key, raw_data.get("app_id"), ctx)
    response, data_params = handle_text_filter(raw_data, ctx)

    request_ip = request.client.host if request.client else ""

    response["extra"]["client_ip"] = request_ip

    try:
        submit_kafka(data_params, response, ctx)
    except Exception as err:
        ctx.logger.debug(f"submit kafka error: {err}")

    return response
