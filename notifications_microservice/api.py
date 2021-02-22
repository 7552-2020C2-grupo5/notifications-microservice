"""API module."""
import logging

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushResponseError,
    PushServerError,
)
from flask_restx import Api, Resource, fields, reqparse

from notifications_microservice import __version__
from notifications_microservice.controller import (
    register_user_token,
    schedule_notification,
    send_notification,
)
from notifications_microservice.exceptions import UserTokenDoesNotExist
from notifications_microservice.utils import IntegerOrStringField

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(
    prefix="/v1",
    version=__version__,
    validate=True,
    title="Notifications API",
    description="Notifications microservice for bookbnb",
    default="Notifications",
    default_label="Notifications operations",
)


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised."""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)


notifications_model = api.model(
    "Notification model",
    {
        "to": fields.Integer(required=True, location="json"),
        "title": fields.String(required=True, location="json"),
        "body": fields.String(required=True, location="json"),
        "data": fields.Wildcard(IntegerOrStringField, required=False, location="json"),
    },
)

scheduled_notifications_model = api.clone(
    "Scheduled notification model",
    notifications_model,
    {
        "at": fields.DateTime(
            required=True, help="UTC ISO 8601 datetime to send the notification at"
        )
    },
)

user_token_parser = reqparse.RequestParser()
user_token_parser.add_argument(
    "user_id",
    type=int,
    help="User id the token belongs to",
    required=True,
    location="json",
)
user_token_parser.add_argument(
    "push_token",
    type=str,
    help="The token used for push notifications",
    required=True,
    location="json",
)


@api.route("/notifications")
class NotificationsResource(Resource):
    """Notification Resource."""

    @api.doc('push_notification')
    @api.expect(notifications_model)
    def post(self):
        """Create a new notification."""
        try:
            send_notification(**api.payload)
        except UserTokenDoesNotExist as e:
            return {"message": str(e)}, 400
        except DeviceNotRegisteredError:
            return {"message": "Invalid registered token"}, 400  # TODO: better error
        except (PushResponseError, PushServerError) as e:
            return {"message": str(e)}, 500


@api.route("/scheduled_notifications")
class ScheduledNotifications(Resource):
    """Scheduled Notification Resource."""

    @api.doc('scheduled_push_notifications')
    @api.expect(scheduled_notifications_model)
    def post(self):
        """Create a new scheduled notification."""
        schedule_notification(**api.payload)


@api.route("/user_token")
class UserTokenResource(Resource):
    """User Token Resource."""

    @api.doc('user_token')
    @api.expect(user_token_parser)
    def put(self):
        """Register token to user."""
        register_user_token(**user_token_parser.parse_args())
