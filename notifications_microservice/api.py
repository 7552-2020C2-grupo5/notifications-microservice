"""API module."""
import logging

from flask_restx import Api, Resource, inputs, reqparse

from notifications_microservice import __version__
from notifications_microservice.controller import (
    register_user_token,
    schedule_notification,
    send_notification,
)

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


notifications_parser = reqparse.RequestParser()
notifications_parser.add_argument(
    "to",
    type=int,
    help='User id that will receive the notification',
    required=True,
    location="json",
)
notifications_parser.add_argument(
    'title', type=str, help='Title for the notification', required=True, location="json"
)
notifications_parser.add_argument(
    'body', type=str, help='Body for the notification', required=True, location="json"
)

scheduled_notification_parser = notifications_parser.copy()
scheduled_notification_parser.add_argument(
    'at',
    type=inputs.datetime_from_iso8601,
    help='Datetime at which to send the notification',
    required=True,
    location="json",
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
    @api.expect(notifications_parser)
    def post(self):
        """Create a new notification."""
        send_notification(**notifications_parser.parse_args())


@api.route("/scheduled_notifications")
class ScheduledNotifications(Resource):
    """Scheduled Notification Resource."""

    @api.doc('scheduled_push_notifications')
    @api.expect(scheduled_notification_parser)
    def post(self):
        """Create a new scheduled notification."""
        schedule_notification(**scheduled_notification_parser.parse_args())


@api.route("/user_token")
class UserTokenResource(Resource):
    """User Token Resource."""

    @api.doc('user_token')
    @api.expect(user_token_parser)
    def put(self):
        """Register token to user."""
        register_user_token(**user_token_parser.parse_args())
