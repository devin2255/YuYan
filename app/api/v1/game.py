from fastapi import APIRouter, Depends, Request

from sqlalchemy.orm import Session

from yuyan.app.api.deps import get_ctx, get_db
from yuyan.app.schemas.game import CreateGame, UpdateGame
from yuyan.app.services.response import success_response
from yuyan.app.services.serializer import to_dict
from yuyan.app.services.validators import FormProxy, parse_request_payload
from yuyan.app.services import game_service

router = APIRouter(prefix="/game")


@router.get("/{game_id}")
def get_game(game_id: str, db: Session = Depends(get_db)):
    game = game_service.get_game(db, game_id)
    return success_response(data=to_dict(game))


@router.get("")
def get_games(db: Session = Depends(get_db)):
    games = game_service.get_games(db)
    return success_response(data=to_dict(games))


@router.post("")
async def create_game(request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = CreateGame(**payload)
    form = FormProxy(**form_data.dict())
    access_key = game_service.create_game(db, ctx, form)
    return success_response(msg=f"新建游戏应用成功, access_key: {access_key}")


@router.put("/{game_id}")
async def update_game(game_id: str, request: Request, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    payload = await parse_request_payload(request)
    form_data = UpdateGame(**payload)
    form = FormProxy(**form_data.dict())
    game_service.update_game(db, ctx, game_id, form)
    return success_response(msg="更新游戏应用成功")


@router.delete("/{game_id}")
def delete_game(game_id: str, db: Session = Depends(get_db), ctx=Depends(get_ctx)):
    game_service.delete_game(db, ctx, game_id)
    return success_response(msg="删除游戏应用成功")
