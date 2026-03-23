from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models import Notification


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_notification(
        self,
        *,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        related_type: str | None = None,
        related_id: int | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            notification_type=notification_type,
            related_type=related_type,
            related_id=related_id,
            is_read=False,
        )
        self.db.add(notification)
        self.db.flush()
        return notification

    def list_by_user_id(
        self,
        *,
        user_id: int,
        unread_only: bool = False,
        limit: int = 20,
    ) -> list[Notification]:
        query = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.id.desc())
        )

        if unread_only:
            query = query.filter(Notification.is_read.is_(False))

        return query.limit(limit).all()

    def get_by_id_and_user_id(
        self,
        *,
        notification_id: int,
        user_id: int,
    ) -> Notification | None:
        return (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

    def mark_as_read(
        self,
        *,
        notification: Notification,
    ) -> Notification:
        notification.is_read = True
        notification.read_at = datetime.now()
        self.db.flush()
        return notification

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()