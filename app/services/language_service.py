from sqlalchemy.orm import Session

from yuyan.app.core.exceptions import NotFound, ParameterException
from yuyan.app.models.language import Language


def get_language(db: Session, language_id: int):
    language = db.query(Language).filter(Language.id == language_id, Language.delete_time.is_(None)).first()
    if not language:
        raise NotFound(message="没有找到相关语种")
    return language


def get_languages(db: Session):
    languages = db.query(Language).filter(Language.delete_time.is_(None)).all()
    if not languages:
        raise NotFound(message="没有找到相关语种")
    return languages


def create_language(db: Session, form):
    language = db.query(Language).filter(Language.abbrev == form.abbrev.data, Language.delete_time.is_(None)).first()
    if language:
        raise ParameterException(message="语种已存在")
    new_language = Language(
        abbrev=form.abbrev.data,
        name=form.name.data,
        create_by=form.username.data,
        update_by=form.username.data,
    )
    db.add(new_language)
    db.commit()
    return True


def update_language(db: Session, language_id: int, form):
    language = get_language(db, language_id)
    language.abbrev = form.abbrev.data
    language.name = form.name.data
    language.update_by = form.username.data
    db.add(language)
    db.commit()
    return True


def delete_language(db: Session, language_id: int, form):
    language = get_language(db, language_id)
    language.soft_delete(form.username.data)
    db.add(language)
    db.commit()
    return True
