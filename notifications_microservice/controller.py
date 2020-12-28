"""Logic for the microservice."""
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


def send_notification(to, title, body):
    """Send notifications using the appropiate provider."""
    user_token = UserToken.query(user_id=to).first()
    if user_token is None:
        raise UserTokenDoesNotExist
    try:
        response = PushClient().publish(
            PushMessage(to=user_token.push_token, title=title, body=body)
        )
    except (  # pylint: disable= W0706
        PushServerError,
        RequestsConnectionError,
        HTTPError,
    ):
        raise
    try:
        response.validate_response()
    except DeviceNotRegisteredError as exc:
        # TODO: set invalid
        raise NotADirectoryError from exc
    except PushResponseError:  # pylint: disable=W0706
        raise


def schedule_notification(to, title, body, at):
    """Create a new scheduled notification."""
    new_scheduled_notification = ScheduledNotification(
        to=to, title=title, body=body, at=at
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
    for unsent_notification in unsent_notifications:
        send_notification(
            unsent_notifications.to,
            unsent_notifications.title,
            unsent_notifications.body,
        )
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
