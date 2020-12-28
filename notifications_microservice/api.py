"""API module."""
import logging

from flask_restx import Api, Resource, fields

from notifications_microservice import __version__
from notifications_microservice.controller import (
    register_user_token,
    schedule_notification,
    send_notification,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(prefix="/v1", version=__version__, validate=True)


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)


notification_model = api.model(
    'Notification',
    {
        'to': fields.String(description='Token for notification target', required=True),
        'title': fields.String(description='Title for the notification', required=True),
        'body': fields.String(description='Body for the notification', required=True),
    },
)

scheduled_notification_model = api.clone(
    "Scheduled notification",
    notification_model,
    {'at': fields.DateTime(description='Datetime at which to send the notification')},
)


user_token_model = api.model(
    "User token",
    {
        "user_id": fields.Integer(
            description="User id the token belongs to", required=True
        ),
        "push_token": fields.String(
            description="The token used for push notifications", required=True
        ),
    },
)


@api.route("/notifications")
class NotificationsResource(Resource):
    @api.doc('push_notification')
    @api.expect(notification_model)
    def post(self):
        '''Create a new publication'''
        send_notification(**api.payload)


@api.route("/scheduled_notifications")
class ScheduledNotifications(Resource):
    @api.doc('scheduled_push_notifications')
    @api.expect(scheduled_notification_model)
    def post(self):
        schedule_notification(**api.payloadd)


@api.route("/user_token")
class UserTokenResource(Resource):
    @api.doc('user_token')
    @api.expect(user_token_model)
    def put(self):
        """Register token to user"""
        register_user_token(**api.payload)
