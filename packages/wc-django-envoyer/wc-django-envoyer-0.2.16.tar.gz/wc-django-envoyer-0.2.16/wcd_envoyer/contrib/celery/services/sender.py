from typing import *

from django.utils import timezone

from wcd_envoyer.models import Message
from wcd_envoyer.channels import MessageData
from wcd_envoyer.services.sender import Sender


class CelerySender(Sender):
    celery_task_caller: Callable = None

    def send_messages_through_celery(self, message_ids, context):
        Message.objects.filter(pk__in=message_ids).update(
            status=Message.Status.PENDING, updated_at=timezone.now(),
        )

        return self.celery_task_caller(
            message_ids=message_ids, context=context, only_pending=True,
        )

    def send(
        self,
        messages_data: Sequence[MessageData],
        context: dict = {},
        only_channels: Optional[Sequence[str]] = None,
    ):
        messages_groups = self.prepare_messages(
            messages_data, context=context, only_channels=only_channels,
        )

        if len(messages_groups) != 0:
            self.send_messages_through_celery(
                [y.pk for _, _, x in messages_groups for y in x], context,
            )

        return [], []

    def resend(self, messages: Iterable[Message], context: dict = {}):
        self.send_messages_through_celery([x.pk for x in messages], context)
        return [], []
