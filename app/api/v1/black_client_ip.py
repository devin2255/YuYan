from pathlib import Path

from fastapi import APIRouter, Depends, Request

from yuyan.app.api.deps import get_ctx
from yuyan.app.core.exceptions import ParameterException
from yuyan.app.schemas.black_ip import BlackIP
from yuyan.app.services.response import success_response
from yuyan.app.services.validators import FormProxy, parse_request_payload

router = APIRouter(prefix="/black_client_ip")


@router.get("")
def get_black_ips(ctx=Depends(get_ctx)):
    return ctx.config.get("BLACK_CLIENT_IP", [])


@router.post("")
async def create_client_ip(request: Request, ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = BlackIP(**payload)
    form = FormProxy(**form_data.dict())
    ip = form.ip.data
    ip_file = ctx.config.get("BLACK_CLIENT_IP_FILE", "app/config/black_client_ip.txt")
    if not Path(ip_file).exists():
        Path(ip_file).parent.mkdir(parents=True, exist_ok=True)
        Path(ip_file).write_text("", encoding="utf-8")
    with open(ip_file, "r", encoding="utf-8") as f:
        ips = [i.strip() for i in f.readlines()]
        if ip in ips:
            raise ParameterException(msg="ip已存在")

    with open(ip_file, "a", encoding="utf-8") as f:
        f.write(f"{ip}\n")
    ctx.config["BLACK_CLIENT_IP"] = ips + [ip]
    return success_response(msg="新增ip成功")


@router.delete("/delete")
async def delete_client_ip(request: Request, ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = BlackIP(**payload)
    form = FormProxy(**form_data.dict())
    ip = form.ip.data
    ip_file = ctx.config.get("BLACK_CLIENT_IP_FILE", "app/config/black_client_ip.txt")
    if not Path(ip_file).exists():
        Path(ip_file).parent.mkdir(parents=True, exist_ok=True)
        Path(ip_file).write_text("", encoding="utf-8")
    with open(ip_file, "r", encoding="utf-8") as f:
        ips = [i.strip() for i in f.readlines()]
        if ip not in ips:
            raise ParameterException(msg="ip不存在")
    ips.remove(ip)
    with open(ip_file, "w", encoding="utf-8") as f:
        for i in ips:
            f.write(f"{i}\n")
    ctx.config["BLACK_CLIENT_IP"] = ips
    return success_response(msg="删除ip成功")
