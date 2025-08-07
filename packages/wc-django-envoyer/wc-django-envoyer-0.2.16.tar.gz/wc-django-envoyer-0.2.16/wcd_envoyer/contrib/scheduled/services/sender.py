from typing import *
from datetime import datetime
from collections import defaultdict

from django.utils import timezone
from django.db.models import prefetch_related_objects

from wcd_envoyer.channels.backend import BaseMessagingBackend
from wcd_envoyer.services.sender import TemplatedMessagesGroup
from wcd_envoyer.models import ChannelConfig, Message
from wcd_envoyer.contrib.celery.services.sender import CelerySender
from wcd_envoyer.channels import MessageData

from . import scheduler
from ..models import MessageSchedule, EventAvailability


__all__ = 'ScheduledSenderMixin', 'ScheduledCelerySender',


MadeMessagesResult = List[Tuple[BaseMessagingBackend, ChannelConfig, List[Message]]]


class ScheduledSenderMixin:
    NOW_KEY: str = 'now'
    SCHEDULED_KEY: str = '_id_scheduled'
    IMMEDIATE_KEY: str = scheduler.IMMEDIATE_KEY
    TZ_KEY: str = scheduler.TZ_KEY

    def get_channel_configs(self, channels: Sequence[str]):
        configs = super().get_channel_configs(channels)
        prefetch_related_objects(list(configs.values()), 'channel_availability')

        return configs

    def get_event_availability_configs(self):
        availabilities = EventAvailability.objects.all()
        result = defaultdict(list)

        for availability in availabilities:
            for event in availability.events:
                result[event].append(availability)

        return result

    def send_messages(self, messages: Iterable[Message], context: dict = {}):
        succeeded, failed = super().send_messages(messages, context=context)
        succeeded_pks = [y.pk for _, _, x in succeeded for y in x]

        if len(succeeded_pks) > 0:
            MessageSchedule.objects.filter(message_id__in=succeeded_pks).delete()

        return succeeded, failed

    def is_message_scheduled(self, message: Message) -> bool:
        return getattr(message, self.SCHEDULED_KEY, False)

    def split_scheduled_messages(
        self,
        templated_messages: Iterable[TemplatedMessagesGroup],
        context: dict = {},
    ) -> Dict[Optional[datetime], List[TemplatedMessagesGroup]]:
        if getattr(context, self.IMMEDIATE_KEY, False):
            return {None: list(templated_messages)}

        now = context.get(self.NOW_KEY) or timezone.now()
        tz_key = self.TZ_KEY
        splitted = defaultdict(list)
        availability_configs = self.get_event_availability_configs()

        for backend, config, items in templated_messages:
            splitted_items = scheduler.split_scheduled_messages(
                list(config.channel_availability.all()),
                items, now, tz_key=tz_key, immediate_key=self.IMMEDIATE_KEY,
                events_availability=availability_configs,
            )

            for schedule_at, messages in splitted_items.items():
                splitted[schedule_at].append((backend, config, messages))

        splitted[None] = splitted.pop(now, [])

        return splitted

    def make_messages(
        self,
        templated_messages: Iterable[TemplatedMessagesGroup],
        context: dict = {},
    ) -> MadeMessagesResult:
        splitted = self.split_scheduled_messages(
            templated_messages, context=context,
        )
        result = defaultdict(list)
        scheduled = []

        for send_at, data in splitted.items():
            for backend, config, items in data:
                messages = self.make_backend_messages(
                    backend, config, items, context=context,
                )

                if len(messages) > 0:
                    result[(backend, config)] += messages

                    if send_at is not None:
                        scheduled.append((send_at, messages))

        all_messages = Message.objects.bulk_create([
            item
            for items in result.values()
            for item in items
        ])

        if len(scheduled) > 0:
            schedules = MessageSchedule.objects.bulk_create([
                MessageSchedule(message_id=message.pk, send_at=send_at)
                for send_at, messages in scheduled
                for message in messages
            ])
            messages_map = {m.pk: m for m in all_messages}
            set_key = self.SCHEDULED_KEY

            for schedule in schedules:
                message = messages_map[schedule.message_id]
                setattr(message, set_key, True)
                message.schedule = schedule

        return [
            (backend, config, items)
            for (backend, config), items in result.items()
        ]


class ScheduledCelerySender(ScheduledSenderMixin, CelerySender):
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
                [
                    y.pk
                    for _, _, x in messages_groups
                    for y in x
                    if not self.is_message_scheduled(y)
                ],
                context,
            )

        return [], []
