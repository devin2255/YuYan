from sqlalchemy.orm import Session

from app.core.exceptions import NotFound
from app.models.channel import Channel


def get_channel(db: Session, channel_id: int):
    channel = db.query(Channel).filter(Channel.id == channel_id, Channel.delete_time.is_(None)).first()
    if not channel:
        raise NotFound(message="没有找到相关渠道信息")
    return channel


def get_channels(db: Session):
    channels = db.query(Channel).filter(Channel.delete_time.is_(None)).all()
    if not channels:
        raise NotFound(message="没有找到相关渠道信息")
    return channels


def create_channel(db: Session, form):
    new_channel = Channel(
        name=form.name.data,
        memo=form.memo.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(new_channel)
    db.commit()
    return True


def update_channel(db: Session, channel_id: int, form):
    channel = get_channel(db, channel_id)
    channel.name = form.name.data
    channel.memo = form.memo.data
    db.add(channel)
    db.commit()
    return True


def delete_channel(db: Session, channel_id: int):
    channel = get_channel(db, channel_id)
    channel.soft_delete()
    db.add(channel)
    db.commit()
    return True
