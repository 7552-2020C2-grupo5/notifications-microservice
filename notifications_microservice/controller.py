"""Logic for the microservice."""
import logging

from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushResponseError,
    PushServerError,
)
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError

from notifications_microservice.exceptions import UserTokenDoesNotExist
from notifications_microservice.models import ScheduledNotification, UserToken, db

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def send_notification(to, title, body, data):
    """Send notifications using the appropiate provider."""
    user_token = UserToken.query.filter_by(user_id=to).first()
    if user_token is None:
        raise UserTokenDoesNotExist
    try:
        logger.info("Attempting to send notification")
        response = PushClient().publish(
            PushMessage(to=user_token.push_token, title=title, body=body, data=data)
        )
    except (  # pylint: disable= W0706
        PushServerError,
        RequestsConnectionError,
        HTTPError,
    ) as e:
        logger.error(e)
        raise
    try:
        response.validate_response()
    except DeviceNotRegisteredError as e:
        # TODO: set invalid
        logger.error(e)
        raise
    except PushResponseError as e:  # pylint: disable=W0706
        logger.error(e)
        raise


def schedule_notification(to, title, body, data, at):
    """Create a new scheduled notification."""
    new_scheduled_notification = ScheduledNotification(
        to=to, title=title, body=body, at=at, data=data
    )
    db.session.add(new_scheduled_notification)
    db.session.commit()


def send_scheduled_notifications(before):
    """Send all scheduled notifications due."""
    unsent_notifications = (
        ScheduledNotification.query.filter(
            ScheduledNotification.processed == False  # noqa: E712
        )
        .filter(ScheduledNotification.at <= before)
        .all()
    )
    logger.info("%s notifications to be sent", len(unsent_notifications))
    for unsent_notification in unsent_notifications:
        try:
            send_notification(
                unsent_notification.to,
                unsent_notification.title,
                unsent_notification.body,
                unsent_notification.data,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error(e)
        unsent_notification.processed = True
        db.session.merge(unsent_notification)
    db.session.commit()


def register_user_token(user_id, push_token):
    """Register a push token to a user."""
    user_token = UserToken.query.filter(UserToken.user_id == user_id).first()
    if user_token is None:
        user_token = UserToken(user_id=user_id, push_token=push_token)
    else:
        user_token.push_token = push_token
    db.session.merge(user_token)
    db.session.commit()
