from fastapi import APIRouter, Depends

from app.api.deps import get_ctx
from app.core.exceptions import ParameterException
from app.schemas.image import ImageRequest
from app.utils.kafka_utils import submit_img_kafka
from app.services.image_service import handle_image_filter
from app.services.validators import (
    parse_json_string,
    validate_access_key,
)

router = APIRouter(prefix="/moderation")


@router.post("/images")
async def image_filter(payload: ImageRequest, ctx=Depends(get_ctx)):
    access_key = payload.access_key

    raw_data = payload.data
    if raw_data is None:
        raise ParameterException(msg="参数不合法(data is empty)")
    if isinstance(raw_data, str):
        raw_data = parse_json_string(raw_data)

    validate_access_key(access_key, raw_data.get("app_id"), ctx)
    response, data_params = handle_image_filter(raw_data)

    try:
        submit_img_kafka(data_params, response, ctx)
    except Exception as err:
        ctx.logger.debug(f"submit img kafka error: {err}")

    return response
