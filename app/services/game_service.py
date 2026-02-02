import json
import time

from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.game import Game
from yuyan.app.utils.md5_util import generate_md5


def get_game(db: Session, game_id: str):
    game = db.query(Game).filter(Game.game_id == game_id, Game.delete_time.is_(None)).first()
    if not game:
        raise NotFound(message="没有找到相关游戏")
    return game


def get_games(db: Session):
    games = db.query(Game).filter(Game.delete_time.is_(None)).all()
    if not games:
        raise NotFound(message="没有找到相关游戏")
    return games


def create_game(db: Session, ctx, form):
    game = db.query(Game).filter(Game.game_id == form.game_id.data, Game.delete_time.is_(None)).first()
    if game:
        raise ParameterException(message="游戏已存在")

    access_key = generate_md5(str(form.game_id.data) + str(int(time.time() * 1000)))
    new_game = Game(
        game_id=form.game_id.data,
        name=form.name.data,
        access_key=access_key,
        dun_secret_id=form.dun_secret_id.data,
        dun_secret_key=form.dun_secret_key.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(new_game)
    db.commit()

    redis_client = ctx.config["REDIS_CLIENT"]
    redis_client.sadd("all_games", form.game_id.data)
    redis_client.hset("access_key", form.game_id.data, access_key)
    redis_client.hset(
        "dun_secret",
        form.game_id.data,
        json.dumps({"secret_id": form.dun_secret_id.data, "secret_key": form.dun_secret_key.data}),
    )
    ctx.config.setdefault("ALL_GAMES", []).append(form.game_id.data)
    ctx.config.setdefault("ACCESS_KEY", {})[form.game_id.data] = access_key
    ctx.config.setdefault("DUN_SECRET", {})[form.game_id.data] = {
        "secret_id": form.dun_secret_id.data,
        "secret_key": form.dun_secret_key.data,
    }
    return access_key


def update_game(db: Session, ctx, game_id: str, form):
    game = get_game(db, game_id)
    game.name = form.name.data
    game.dun_secret_id = form.dun_secret_id.data
    game.dun_secret_key = form.dun_secret_key.data
    game.update_by = form.username.data
    db.add(game)
    db.commit()

    redis_client = ctx.config["REDIS_CLIENT"]
    redis_client.hset(
        "dun_secret",
        game_id,
        json.dumps({"secret_id": form.dun_secret_id.data, "secret_key": form.dun_secret_key.data}),
    )
    ctx.config.setdefault("DUN_SECRET", {})[game_id] = {
        "secret_id": form.dun_secret_id.data,
        "secret_key": form.dun_secret_key.data,
    }
    return True


def delete_game(db: Session, ctx, game_id: str):
    game = get_game(db, game_id)
    game.soft_delete()
    db.add(game)
    db.commit()

    redis_client = ctx.config["REDIS_CLIENT"]
    redis_client.srem("all_games", game_id)
    redis_client.hdel("access_key", game_id)
    redis_client.hdel("dun_secret", game_id)
    ctx.config.setdefault("ALL_GAMES", [])
    if game_id in ctx.config["ALL_GAMES"]:
        ctx.config["ALL_GAMES"].remove(game_id)
    if ctx.config.get("ACCESS_KEY"):
        ctx.config["ACCESS_KEY"].pop(game_id, None)
    if ctx.config.get("DUN_SECRET"):
        ctx.config["DUN_SECRET"].pop(game_id, None)
    return True
