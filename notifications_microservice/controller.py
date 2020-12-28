"""Logic for the microservice."""
from notifications_microservice.models import ScheduledNotification, UserToken, db


def send_notification(_to, _title, _body):
    pass


def schedule_notification(to, title, body, at):
    new_scheduled_notification = ScheduledNotification(
        to=to, title=title, body=body, at=at
    )
    db.session.add(new_scheduled_notification)
    db.session.commit()


def send_scheduled_notifications(before):
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
    new_user_token = UserToken(user_id=user_id, push_token=push_token)
    db.session.add(new_user_token)
    db.session.commit()
