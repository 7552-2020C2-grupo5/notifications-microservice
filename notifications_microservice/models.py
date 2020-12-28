"""SQLAlchemy models."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ScheduledNotification(db.Model):  # type: ignore
    """Scheduled notifications model."""

    id = db.Column(db.Integer, primary_key=True)
    to = db.Column(db.String)
    title = db.Column(db.String)
    body = db.Column(db.String)
    at = db.Column(db.DateTime)
    processed = db.Column(db.Boolean, default=False)


class UserToken(db.Model):  # type: ignore
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    push_token = db.Column(db.String)
