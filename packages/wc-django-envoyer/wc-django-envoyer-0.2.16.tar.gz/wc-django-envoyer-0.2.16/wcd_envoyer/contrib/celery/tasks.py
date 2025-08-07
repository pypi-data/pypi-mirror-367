from typing import *

from wcd_envoyer.contrib.celery.services.sender import CelerySender
from wcd_envoyer.models import Message


__all__ = 'actual_sending_messages_task',


def actual_sending_messages_task(
    sender: CelerySender,
    message_ids: List[int] = [],
    context: dict = {},
    only_pending: bool = False,
    callback: Optional[Callable] = None,
):
    messages = Message.objects.filter(pk__in=message_ids)

    if only_pending:
        messages = messages.filter(status=Message.Status.PENDING)

    result = sender.send_messages(messages, context=context)

    if callback is not None:
        callback(result, context)
