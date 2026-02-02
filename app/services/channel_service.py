from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.channel import Channel


def get_channel(db: Session, no: str):
    channel = db.query(Channel).filter(Channel.no == no, Channel.delete_time.is_(None)).first()
    if not channel:
        raise NotFound(message="没有找到相关渠道信息")
    return channel


def get_channels(db: Session):
    channels = db.query(Channel).filter(Channel.delete_time.is_(None)).all()
    if not channels:
        raise NotFound(message="没有找到相关渠道信息")
    return channels


def create_channel(db: Session, form):
    channel = db.query(Channel).filter(Channel.no == form.no.data, Channel.delete_time.is_(None)).first()
    if channel:
        raise ParameterException(message="渠道信息已存在")

    new_channel = Channel(
        no=form.no.data,
        name=form.name.data,
        memo=form.memo.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(new_channel)
    db.commit()
    return True


def update_channel(db: Session, no: str, form):
    channel = get_channel(db, no)
    channel.name = form.name.data
    channel.memo = form.memo.data
    db.add(channel)
    db.commit()
    return True


def delete_channel(db: Session, no: str):
    channel = get_channel(db, no)
    channel.soft_delete()
    db.add(channel)
    db.commit()
    return True
