from django.db import models
from django.utils.translation import pgettext_lazy

from wcd_notifications.compat import JSONField
from pxd_lingua import create_translated_model

from .. import channels, events
from ..utils import DynamicChoicesField, get_json_encoder
from ..const import MessageStatus
from .utils import DateTimeModel


__all__ = 'Message', 'Template', 'TemplateTranslation',


class Template(DateTimeModel):
    class Meta:
        unique_together = ('channel', 'event'),
        verbose_name = pgettext_lazy('wcd_envoyer', 'Template')
        verbose_name_plural = pgettext_lazy('wcd_envoyer', 'Templates')
        indexes = [
            models.Index(fields=['channel', 'event']),
            models.Index(fields=['is_active']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
        ]

    channel = DynamicChoicesField(
        pgettext_lazy('wcd_envoyer', 'Channel'),
        max_length=512, choices=channels.registry.get_choices,
    )
    event = DynamicChoicesField(
        pgettext_lazy('wcd_envoyer', 'Event'),
        max_length=512, choices=events.registry.get_choices,
    )
    data = JSONField(
        pgettext_lazy('wcd_envoyer', 'Data'), default=dict,
        blank=True, null=False, encoder=get_json_encoder(),
    )

    is_active = models.BooleanField(
        pgettext_lazy('wcd_envoyer', 'Is active'), default=False,
    )

    def __str__(self) -> str:
        return pgettext_lazy('wcd_envoyer', '{channel}: {event}').format(
            channel=self.get_channel_display(),
            event=self.get_event_display(),
        )


class Message(DateTimeModel):
    Status = MessageStatus

    class Meta:
        verbose_name = pgettext_lazy('wcd_envoyer', 'Message')
        verbose_name_plural = pgettext_lazy('wcd_envoyer', 'Messages')
        ordering = '-created_at',
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['channel', 'event']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
        ]

    status = models.CharField(
        pgettext_lazy('wcd_envoyer', 'Status'),
        max_length=512, default=MessageStatus.NEW,
        choices=MessageStatus.choices,
    )
    channel = DynamicChoicesField(
        pgettext_lazy('wcd_envoyer', 'Channel'),
        max_length=512, choices=channels.registry.get_choices,
    )
    event = DynamicChoicesField(
        pgettext_lazy('wcd_envoyer', 'Event'),
        max_length=512, choices=events.registry.get_choices,
    )
    recipients = JSONField(
        pgettext_lazy('wcd_envoyer', 'Recipients'),
        default=list, blank=False, null=False,
    )
    data = JSONField(
        pgettext_lazy('wcd_envoyer', 'Data'), default=dict,
        blank=True, null=False, encoder=get_json_encoder(),
    )

    def __str__(self) -> str:
        return pgettext_lazy('wcd_envoyer', 'Message #{id}: {status}').format(
            id=self.pk, status=self.get_status_display(),
        )


TemplateTranslation = create_translated_model(
    Template, fields=('data',)
)
