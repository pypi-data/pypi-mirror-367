from django import forms

from wcd_envoyer.models import Template, ChannelConfig


__all__ = 'AddTemplateForm', 'AddConfigForm',


class AddTemplateForm(forms.ModelForm):
    class Meta:
        fields = 'channel', 'event', 'is_active',
        model = Template


class AddConfigForm(forms.ModelForm):
    class Meta:
        fields = 'channel', 'is_active',
        model = ChannelConfig
