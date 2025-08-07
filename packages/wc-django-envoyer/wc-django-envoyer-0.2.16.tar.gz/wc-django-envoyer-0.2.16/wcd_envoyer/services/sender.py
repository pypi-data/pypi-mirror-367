from typing import *
import traceback
import logging
from collections import defaultdict

from django.utils.translation import get_language, override
from django.utils import timezone

from wcd_envoyer.events import EventRegistry, registry as events_registry
from wcd_envoyer.channels import (
    FailedMessages,
    BaseMessagingBackend, MessageData, TemplatedMessages, ChannelRegistry,
    registry as channels_registry
)
from wcd_envoyer.const import MessageStatus
from wcd_envoyer.utils import KwargsInjector, sort_and_group
from wcd_envoyer.models import Message, ChannelConfig
from wcd_envoyer.signals import (
    messages_sent, messages_sent_failed, messages_sent_succeeded,
)

from .templates_resolver import TemplatesResolver


__all__ = (
    'TemplatedMessagesGroup', 'MessagesGroup',
    'SucceededMessagesGroup', 'FailedMessagesGroup',
    'Sender',
)

TemplatedMessagesGroup = Tuple[
    BaseMessagingBackend, ChannelConfig, TemplatedMessages
]
MessagesGroup = Tuple[BaseMessagingBackend, ChannelConfig, List[Message]]
SucceededMessagesGroup = Tuple[BaseMessagingBackend, ChannelConfig, List[Message]]
FailedMessagesGroup = Tuple[BaseMessagingBackend, ChannelConfig, FailedMessages]


class Sender(KwargsInjector):
    channels_registry: ChannelRegistry = channels_registry
    events_registry: EventRegistry = events_registry
    templates_resolver: TemplatesResolver = TemplatesResolver()

    def __init__(
        self,
        channels_registry: Optional[ChannelRegistry] = None,
        events_registry: Optional[EventRegistry] = None,
        **kwargs
    ):
        super().__init__(
            channels_registry=channels_registry,
            events_registry=events_registry,
            **kwargs,
        )

    def get_backends(self, only_channels: Optional[Sequence[str]] = None):
        return {
            key: descriptor.backend
            for key, descriptor in self.channels_registry.items()
            if only_channels is None or key in only_channels
        }

    def get_channel_configs(self, channels: Sequence[str]):
        return {
            x.channel: x
            for x in ChannelConfig.objects.filter(
                channel__in=channels, is_active=True,
            )
        }

    def make_templated_messages(
        self,
        backends: Dict[str, BaseMessagingBackend],
        configs: Dict[str, ChannelConfig],
        messages_data: Sequence[MessageData],
    ) -> List[TemplatedMessagesGroup]:
        templates = self.templates_resolver.get_templates({
            (data.channel, data.event)
            for data in messages_data
            if data.channel in backends
        })

        grouped: Dict[str, TemplatedMessages] = defaultdict(list)

        for data in messages_data:
            template = templates.get((data.channel, data.event))

            if template is not None:
                grouped[data.channel].append((data, template))

        return [
            (backends[channel], configs[channel], data)
            for channel, data in grouped.items()
            if channel in backends and channel in configs
        ]

    def make_backend_messages(
        self,
        backend: BaseMessagingBackend,
        config: ChannelConfig,
        items: TemplatedMessages,
        context: dict = {},
    ) -> List[Message]:
        return backend.make_messages(
            config, items, context=context,
        )

    def make_messages(
        self,
        templated_messages: Iterable[TemplatedMessagesGroup],
        context: dict = {},
    ) -> List[Tuple[BaseMessagingBackend, ChannelConfig, List[Message]]]:
        result = []

        for backend, config, items in templated_messages:
            messages = self.make_backend_messages(
                backend, config, items, context=context,
            )

            if len(messages) > 0:
                result.append((backend, config, messages))

        Message.objects.bulk_create([
            item
            for _, _, items in result
            for item in items
        ])

        return result

    def prepare_messages(
        self,
        messages_data: Sequence[MessageData],
        context: dict = {},
        only_channels: Optional[Sequence[str]] = None,
    ):
        if len(messages_data) == 0:
            return []

        language = context.get('language', None) or get_language()
        context['language'] = language

        with override(language=language):
            backends = self.get_backends(only_channels=only_channels)
            configs = self.get_channel_configs(backends.keys())
            templated_messages = self.make_templated_messages(
                backends, configs, messages_data,
            )
            return self.make_messages(
                templated_messages, context=context,
            )

    def update_messages_status(
        self, status: MessageStatus, messages: Sequence['Message'],
        only_for_status: Optional[MessageStatus] = None, skip_db: bool = False,
    ):
        for message in messages:
            if (
                only_for_status is None
                or
                message.status == only_for_status
            ):
                message.status = status
                message.updated_at = timezone.now()

        if not skip_db:
            Message.objects.bulk_update(messages, fields=['status', 'updated_at'])

        return messages

    def send_messages_groups(
        self,
        messages_groups: List[MessagesGroup],
        context: dict = {},
    ) -> Tuple[List[SucceededMessagesGroup], List[FailedMessagesGroup]]:
        # TODO: Too complex and self-repetitive method, should be
        # changed somehow...
        succeeded: List[SucceededMessagesGroup] = []
        failed: List[FailedMessagesGroup] = []

        self.update_messages_status(MessageStatus.PENDING, [
            x
            for _, _, messages in messages_groups
            for x in messages
        ])

        for backend, config, messages in messages_groups:
            try:
                c_succeeded, c_failed = backend.send(
                    config, messages, context=context,
                )
            except Exception as e:
                error = {
                    'exception': e, 'message': str(e),
                    'traceback': traceback.format_exc(),
                }
                c_succeeded = []
                c_failed = [(x, error) for x in messages]

            if len(c_succeeded) > 0:
                succeeded.append((backend, config, c_succeeded))

            if len(c_failed) > 0:
                failed.append((backend, config, c_failed))

        all_succeeded = [y for _, _, x in succeeded for y in x]
        all_failed = [y for _, _, x in failed for y in x]

        self.update_messages_status(
            MessageStatus.SENT,
            # FIXME: WEIRD! But only 1 query instead of 2.
            (
                all_succeeded
                +
                self.update_messages_status(
                    MessageStatus.FAILED, [x for x, _ in all_failed],
                    only_for_status=MessageStatus.PENDING, skip_db=True,
                )
            ),
            only_for_status=MessageStatus.PENDING,
        )

        try:
            if len(succeeded) > 0:
                messages_sent_succeeded.send(
                    self, messages_groups=succeeded, messages=all_succeeded,
                    context=context,
                )

            if len(failed) > 0:
                messages_sent_failed.send(
                    self, messages_groups=failed, messages=all_failed,
                    context=context,
                )

            messages_sent.send(
                self,
                succeeded_messages_groups=succeeded,
                failed_messages_groups=failed,
                messages=all_succeeded + all_failed,
                context=context,
            )
        except Exception as e:
            logging.exception(e)

        return succeeded, failed

    def send_messages(self, messages: Iterable[Message], context: dict = {}):
        backends = self.get_backends()
        configs = self.get_channel_configs(backends.keys())

        return self.send_messages_groups(
            [
                (backends[channel], configs[channel], list(messages))
                for channel, messages in sort_and_group(
                    messages, lambda x: x.channel
                )
                if channel in backends and channel in configs
            ],
            context=context,
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

        if len(messages_groups) == 0:
            return [], []

        return self.send_messages_groups(messages_groups, context=context)

    def resend(self, messages: Iterable[Message], context: dict = {}):
        return self.send_messages(messages, context=context)
