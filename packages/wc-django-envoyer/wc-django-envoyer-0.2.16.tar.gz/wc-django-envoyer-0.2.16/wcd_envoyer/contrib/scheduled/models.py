from django.db import models

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import pgettext_lazy

from wcd_envoyer import channels, events
from wcd_envoyer.models import Message, ChannelConfig
from wcd_envoyer.utils import DynamicChoicesField


__all__ = 'MessageSchedule', 'ChannelAvailability', 'EventAvailability',


class ChoiceArrayField(ArrayField):
    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.MultipleChoiceField,
            'choices': self.base_field.choices,
        }
        defaults.update(kwargs)
        return super(ArrayField, self).formfield(**defaults)


class MessageSchedule(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('wcd_envoyer', 'Message schedule')
        verbose_name_plural = pgettext_lazy('wcd_envoyer', 'Message schedules')

    message = models.OneToOneField(
        Message, on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('wcd_envoyer', 'Message'),
        related_name='schedule',
    )
    send_at = models.DateTimeField(
        pgettext_lazy('wcd_envoyer', 'Send at'), null=False, blank=False,
    )

    def __str__(self) -> str:
        return pgettext_lazy('wcd_envoyer', '#{id}: {send_at}').format(
            id=self.message_id, send_at=self.send_at.isoformat(),
        )


class ChannelAvailability(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('wcd_envoyer', 'Channel availability')
        verbose_name_plural = pgettext_lazy('wcd_envoyer', 'Channel availabilities')

    config = models.ForeignKey(
        ChannelConfig, on_delete=models.CASCADE,
        verbose_name=pgettext_lazy('wcd_envoyer', 'Channel config'),
        related_name='channel_availability',
    )
    available_since = models.TimeField(
        pgettext_lazy('wcd_envoyer', 'Available since'),
        null=False, blank=False,
    )
    available_till = models.TimeField(
        pgettext_lazy('wcd_envoyer', 'Available till'),
        null=False, blank=False,
    )

    def __str__(self):
        return f'#{self.id}'


class EventAvailability(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('wcd_envoyer', 'Event availability')
        verbose_name_plural = pgettext_lazy('wcd_envoyer', 'Event availabilities')

    events = ChoiceArrayField(
        DynamicChoicesField(
            max_length=512, choices=events.registry.get_choices,
        ),
        verbose_name=pgettext_lazy('wcd_envoyer', 'Events'),
        blank=False,
        null=False,
    )
    available_since = models.TimeField(
        pgettext_lazy('wcd_envoyer', 'Available since'),
        null=False, blank=False,
    )
    available_till = models.TimeField(
        pgettext_lazy('wcd_envoyer', 'Available till'),
        null=False, blank=False,
    )

    def __str__(self):
        return f'#{self.id}'
