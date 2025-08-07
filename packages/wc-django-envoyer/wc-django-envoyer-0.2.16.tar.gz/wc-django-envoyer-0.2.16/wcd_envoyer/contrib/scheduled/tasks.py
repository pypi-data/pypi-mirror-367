from typing import *
from datetime import datetime, timedelta

from django.utils import timezone
from wcd_envoyer.models import Message

from .services.sender import ScheduledCelerySender
from .models import MessageSchedule


__all__ = 'actual_scheduled_sending_messages_task',


def actual_scheduled_sending_messages_task(
    sender: ScheduledCelerySender,
    now: Optional[datetime] = None,
    delta_seconds: float = timedelta(hours=1).total_seconds(),
    context: dict = {},
    only_new: bool = True,
    callback: Optional[Callable] = None,
):
    now = timezone.now() if now is None else now
    delta = timedelta(seconds=delta_seconds)
    since = now - delta
    messages = Message.objects.filter(pk__in=MessageSchedule.objects.filter(
        send_at__gte=since, send_at__lte=now,
    ).values('message_id'))

    if only_new:
        messages = messages.filter(status=Message.Status.NEW)

    result = sender.send_messages(messages, context=context)

    if callback is not None:
        callback(result, context)
