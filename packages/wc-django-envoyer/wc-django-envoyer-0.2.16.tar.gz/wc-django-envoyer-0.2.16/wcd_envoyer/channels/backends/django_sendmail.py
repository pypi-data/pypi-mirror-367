from typing import *
import traceback

from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils.translation import pgettext_lazy
from django.contrib.postgres.forms import SimpleArrayField

from wcd_envoyer.channels.backend import (
    BaseMessagingBackend, BaseMessagesMaker, SplitRecipientsMessagesMaker,
)
from wcd_envoyer.channels.forms import BaseTemplateForm, BaseConfigForm
from wcd_envoyer.utils import importable_prop
from wcd_envoyer.models import Message, ChannelConfig


__all__ = 'SendMailTemplateForm', 'SendMailBackend',


class SendMailConfigForm(BaseConfigForm):
    class Meta(BaseConfigForm.Meta):
        entangled_fields = {'data': ['from_email', 'reply_to']}

    from_email = forms.CharField(
        label=pgettext_lazy('wcd_envoyer', 'From email'),
        initial='', required=False,
    )
    reply_to = SimpleArrayField(
        base_field=forms.CharField(), delimiter=',',
        label=pgettext_lazy('wcd_envoyer', 'Reply to'),
        initial=[], required=False,
    )


class SendMailTemplateForm(BaseTemplateForm):
    renderable_fields = ['subject', 'plain_text', 'content']

    class Meta(BaseTemplateForm.Meta):
        entangled_fields = {'data': ['subject', 'plain_text', 'content']}

    subject = forms.CharField(
        label=pgettext_lazy('wcd_envoyer', 'Subject'),
    )
    content = forms.CharField(
        label=pgettext_lazy('wcd_envoyer', 'Content'),
        widget=forms.Textarea(),
    )
    plain_text = forms.CharField(
        label=pgettext_lazy('wcd_envoyer', 'Plain text'),
        widget=forms.Textarea(),
        initial='', required=False,
    )


class SendMailBackend(BaseMessagingBackend):
    content_type = 'text/html'
    recipient_resolver = importable_prop(lambda x: x.get('email'))
    config_form_class = importable_prop(SendMailConfigForm)
    template_form_class = importable_prop(SendMailTemplateForm)
    messages_maker_class: Type[BaseMessagesMaker] = importable_prop(
        SplitRecipientsMessagesMaker
    )

    def get_default_from_email(self):
        if 'des' in settings.INSTALLED_APPS:
            from des.models import DynamicEmailConfiguration
            return DynamicEmailConfiguration.get_solo().from_email

        return settings.DEFAULT_FROM_EMAIL

    def create_email(
        self,
        config: ChannelConfig,
        message: Message,
        context: dict = {}
    ) -> EmailMultiAlternatives:
        data = message.data
        config_data = config.data
        content = data.get('content')
        alternatives = []

        if content:
            alternatives.append((content, self.content_type))

        return EmailMultiAlternatives(
            subject=data.get('subject', ''),
            body=data.get('plain_text', ''),
            from_email=(
                config_data.get('from_email', None)
                or
                self.get_default_from_email()
                or
                None
            ),
            to=message.recipients,
            alternatives=alternatives,
            reply_to=config_data.get('reply_to', None) or None,
        )

    def create_emails(
        self,
        config: ChannelConfig,
        messages: Sequence[Message],
        context: dict = {}
    ) -> List[Tuple[Message, EmailMultiAlternatives]]:
        return [
            (message, self.create_email(config, message, context))
            for message in messages
        ]

    def send(
        self,
        config: ChannelConfig,
        messages: Sequence[Message],
        context: dict = {},
    ):
        emails = self.create_emails(config, messages, context=context)
        sent, failed = [], []

        try:
            with get_connection(fail_silently=False) as connection:
                for message, email in emails:
                    try:
                        count = connection.send_messages([email])

                        if count == 1:
                            sent.append(message)
                        else:
                            failed.append((message, None))
                    except Exception as e:
                        failed.append((message, {
                            'exception': e, 'message': str(e),
                            'traceback': traceback.format_exc(),
                        }))

        except Exception as e:
            return [], [(x, e) for x in messages]

        return sent, failed
