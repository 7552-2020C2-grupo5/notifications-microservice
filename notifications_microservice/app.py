"""Flask api."""
import logging
from datetime import datetime as dt
from pathlib import Path

import requests
from flask import Flask, request
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from notifications_microservice.api import api
from notifications_microservice.cfg import config
from notifications_microservice.constants import DEFAULT_VERIFICATION_URL
from notifications_microservice.controller import send_scheduled_notifications
from notifications_microservice.models import db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fix_dialect(s):
    if s.startswith("postgres://"):
        s = s.replace("postgres://", "postgresql://")
    s = s.replace("postgresql://", "postgresql+psycopg2://")
    return s


def before_request():
    excluded_paths = [
        "/",
        "/v1/swagger.json",
        "/swagger.json",
        "/swaggerui/favicon-32x32.png",
        "/swaggerui/swagger-ui-standalone-preset.js",
        "/swaggerui/swagger-ui-standalone-preset.js",
        "/swaggerui/swagger-ui-bundle.js",
        "/swaggerui/swagger-ui.css",
        "/swaggerui/droid-sans.css",
    ]
    if (
        config.env(default="DEV") == "DEV"
        or request.path in excluded_paths
        or request.method == "OPTIONS"
    ):
        return

    bookbnb_token = request.headers.get("BookBNBAuthorization")
    if bookbnb_token is None:
        return {"message": "BookBNB token is missing"}, 401

    r = requests.post(
        config.token_verification_url(default=DEFAULT_VERIFICATION_URL),
        json={"token": bookbnb_token},
        headers={"BookBNBAuthorization": config.bookbnb_token(default="_")},
    )

    if not r.ok:
        return {"message": "Invalid BookBNB token"}, 401


def create_app(test_db=None):
    """creates a new app instance"""
    new_app = Flask(__name__)
    new_app.config["SQLALCHEMY_DATABASE_URI"] = config.database.url(
        default=test_db or "sqlite:///notifications_microservice.db", cast=fix_dialect
    )
    new_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(new_app)
    api.init_app(new_app)
    Migrate(new_app, db, directory=Path(__file__).parent / "migrations")
    new_app.wsgi_app = ProxyFix(
        new_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )  # remove after flask-restx > 0.2.0 is released
    # https://github.com/python-restx/flask-restx/issues/230
    new_app.before_request(before_request)
    CORS(new_app)
    return new_app


if __name__ == '__main__':
    with create_app().app_context():
        before = dt.utcnow()
        send_scheduled_notifications(before)
