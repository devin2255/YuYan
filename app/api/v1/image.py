from fastapi import APIRouter, Depends, Request

from yuyan.app.api.deps import get_ctx
from yuyan.app.core.exceptions import ParameterException
from yuyan.app.utils.kafka_utils import submit_img_kafka
from yuyan.app.services.image_service import handle_image_filter
from yuyan.app.services.validators import (
    parse_json_string,
    parse_request_payload,
    validate_access_key,
)

router = APIRouter()


@router.api_route("/imgfilter.anti", methods=["GET", "POST"])
async def image_filter(request: Request, ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    access_key = payload.get("accessKey")

    raw_data = payload.get("data")
    if raw_data is None:
        raise ParameterException(msg="参数不合法(data is empty)")
    if isinstance(raw_data, str):
        raw_data = parse_json_string(raw_data)

    validate_access_key(access_key, raw_data.get("gameId"), ctx)
    response, data_params = handle_image_filter(raw_data)

    try:
        submit_img_kafka(data_params, response, ctx)
    except Exception as err:
        ctx.logger.debug(f"submit img kafka error: {err}")

    return response
