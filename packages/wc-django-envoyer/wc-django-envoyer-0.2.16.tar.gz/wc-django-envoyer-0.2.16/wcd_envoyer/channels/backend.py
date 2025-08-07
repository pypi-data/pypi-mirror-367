from typing import *
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

from wcd_envoyer.utils import importable_prop, KwargsInjector

if TYPE_CHECKING:
    from wcd_envoyer.models import Message, Template, ChannelConfig


__all__ = (
    'Recipient', 'Recipients',  'TemplatedMessage', 'TemplatedMessages',
    'FailedMessages', 'SucceededFailedMessages',
    'MessageData',
    'BaseMessagesMaker', 'MessagesMaker', 'SplitRecipientsMessagesMaker',
    'MultiRecipientsMessagesMakerMixin', 'SplitRecipientsMessagesMakerMixin',
    'BaseMessagingBackend',
)

Recipient = Dict[str, Any]
Recipients = Sequence[Recipient]
TemplatedMessage = Tuple['MessageData', 'Template']
TemplatedMessages = List[TemplatedMessage]
FailedMessages = List[Tuple['Message', Any]]
SucceededFailedMessages = Tuple[List['Message'], FailedMessages]


@dataclass
class MessageData:
    channel: str
    event: str
    recipients: Recipients
    context: dict = field(default_factory=dict)


class BaseMessagesMaker:
    def __init__(self, backend, recipients_resolver, template_renderer):
        self.recipients_resolver = recipients_resolver
        self.template_renderer = template_renderer

    def normalize_message_data(
        self,
        config: 'ChannelConfig',
        message_data: MessageData,
        context: dict = {},
    ):
        yield message_data

    def make_message(
        self,
        message_data: MessageData,
        template: 'Template',
        context: dict = {}
    ) -> 'Message':
        # FIXME: Circular import...

        from wcd_envoyer.models import Message
        data = {**context, **message_data.context}
        rendered = self.template_renderer(template, context=data)

        return Message(
            channel=message_data.channel,
            event=message_data.event,
            recipients=message_data.recipients,
            data={**data, **rendered}
        )

    def __call__(
        self,
        config: 'ChannelConfig',
        templated_messages: TemplatedMessages,
        context: dict = {},
    ) -> List['Message']:
        messages = []

        for message_data, template in templated_messages:
            for data in self.normalize_message_data(
                config, message_data, context=context,
            ):
                messages.append(self.make_message(data, template, context))

        return messages


class MultiRecipientsMessagesMakerMixin:
    def normalize_message_data(
        self,
        config: 'ChannelConfig',
        message_data: MessageData,
        context: dict = {},
    ):
        recipients = self.recipients_resolver(message_data.recipients)

        if len(recipients) == 0:
            return

        yield MessageData(
            message_data.channel,
            message_data.event,
            recipients=recipients,
            context=message_data.context,
        )


class SplitRecipientsMessagesMakerMixin:
    def normalize_message_data(
        self,
        config: 'ChannelConfig',
        message_data: MessageData,
        context: dict = {},
    ):
        for recipient in self.recipients_resolver(message_data.recipients):
            yield MessageData(
                message_data.channel,
                message_data.event,
                recipients=[recipient],
                context=message_data.context,
            )


class MessagesMaker(MultiRecipientsMessagesMakerMixin, BaseMessagesMaker):
    pass


class SplitRecipientsMessagesMaker(
    SplitRecipientsMessagesMakerMixin, BaseMessagesMaker,
):
    pass


class BaseMessagingBackend(KwargsInjector):
    # FIXME: A bit shitty API here:
    recipient_resolver = importable_prop(lambda x: x)
    config_form_class = importable_prop(
        'wcd_envoyer.channels.forms.BaseConfigForm',
    )
    template_form_class = importable_prop(
        'wcd_envoyer.channels.forms.BaseTemplateForm',
    )
    template_renderer = importable_prop(
        'wcd_envoyer.channels.renderers.django_template_renderer',
    )
    messages_maker_class: Type[BaseMessagesMaker] = importable_prop(
        'wcd_envoyer.channels.backend.MessagesMaker',
    )
    messages_maker: BaseMessagesMaker = cached_property(
        lambda self: self.messages_maker_class(
            self,
            recipients_resolver=self.resolve_recipients,
            template_renderer=self.render_template,
        )
    )

    def resolve_recipients(self, recipients: Recipients):
        resolver = self.recipient_resolver
        resolved = (resolver(recipient) for recipient in recipients)

        return [x for x in resolved if x is not None]

    # TODO: Move template related methods into different class.
    def render_template(self, template: 'Template', context: dict = {}):
        # TODO: Change the way it handles translation
        initial_data = template.data
        template.data = template.translated.data
        renderer = self.template_renderer
        form = self.template_form_class(instance=template)
        data = {**form.initial}

        for field in form.get_renderable_fields():
            data[field] = renderer(data.get(field, ''), {**context, **data})

        template.data = initial_data

        return data

    def make_messages(
        self,
        config: 'ChannelConfig',
        templated_messages: TemplatedMessages,
        context: dict = {},
    ) -> List['Message']:
        return self.messages_maker(config, templated_messages, context=context)

    def send(
        self,
        config: 'ChannelConfig',
        messages: Sequence['Message'],
        context: dict = {},
    ) -> SucceededFailedMessages:
        raise NotImplementedError()
