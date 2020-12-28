"""API module."""
import logging

from flask_restx import Api, Resource, fields

from notifications_microservice import __version__
from notifications_microservice.controller import (
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


notification_resource = api.model(
    'Notification',
    {
        'to': fields.String(description='Token for notification target', required=True),
        'title': fields.String(description='Title for the notification', required=True),
        'body': fields.String(description='Body for the notification', required=True),
    },
)

scheduled_notification_resource = api.clone(
    "Scheduled notification",
    notification_resource,
    {'at': fields.DateTime(description='Datetime at which to send the notification')},
)


@api.route("/notifications")
class NotificationsResource(Resource):
    @api.doc('push_notification')
    @api.expect(notification_resource)
    def post(self):
        '''Create a new publication'''
        send_notification(**api.payload)


@api.route("/scheduled_notifications")
class ScheduledNotifications(Resource):
    @api.doc('scheduled_push_notifications')
    @api.expect(scheduled_notification_resource)
    def post(self):
        schedule_notification(**api.payload)
