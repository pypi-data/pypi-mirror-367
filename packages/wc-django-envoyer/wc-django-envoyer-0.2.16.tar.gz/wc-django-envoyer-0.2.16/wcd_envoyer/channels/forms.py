from typing import *
from django.utils.translation import pgettext_lazy

from entangled.forms import EntangledModelForm
from entangled import forms as entangled_forms

from wcd_notifications.compat import JSONField

from wcd_envoyer.models import ChannelConfig, Template


__all__ = (
    'BaseConfigForm',
    'BaseTemplateForm',
)

# HACK!
entangled_forms.JSONField = JSONField


class BaseConfigForm(EntangledModelForm):
    class Meta:
        entangled_fields = {'data': []}
        model = ChannelConfig
        untangled_fields = ['channel', 'is_active']


class BaseTemplateForm(EntangledModelForm):
    renderable_fields: List[str] = []

    class Meta:
        entangled_fields = {'data': []}
        model = Template
        untangled_fields = ['channel', 'event', 'is_active']

    def get_renderable_fields(self):
        return self.renderable_fields
