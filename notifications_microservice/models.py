"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property
import json
from dateutil import parser as dateutil_parser
from sqlalchemy.orm import validates

db = SQLAlchemy()


class ScheduledNotification(db.Model):  # type: ignore
    """Scheduled notifications model."""

    id = db.Column(db.Integer, primary_key=True)
    to = db.Column(db.Integer)
    title = db.Column(db.String)
    body = db.Column(db.String)
    _data = db.Column(db.String, nullable=True)
    at = db.Column(db.DateTime)
    processed = db.Column(db.Boolean, default=False)

    @validates("at")
    def validate_at(self, _key, val):
        if type(val) is str:
            return dateutil_parser.isoparse(val)
        return val

    @hybrid_property
    def data(self):
        return self._data

    @data.setter  # type: ignore
    def data(self, valdict):
        self._data = json.dumps(valdict)


class UserToken(db.Model):  # type: ignore
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    push_token = db.Column(db.String)
