from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy

from .util import kenya_time

redis = FlaskRedis()
db = SQLAlchemy()


class CRUDMixin(object):
    def __repr__(self):
        return "<{}>".format(self.__class__.__name__)

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def save(self):
        """Saves object to database"""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """deletes object from db"""
        db.session.delete(self)
        db.session.commit()
        return self


class AuditColumns(CRUDMixin):
    created_by = db.Column(db.String(128), nullable=True)
    created_date = db.Column(db.DateTime, default=kenya_time)
    last_edited_date = db.Column(db.DateTime, onupdate=kenya_time, default=kenya_time)
    last_edited_by = db.Column(db.String(128), nullable=True)
    active = db.Column(db.Boolean, default=False)
