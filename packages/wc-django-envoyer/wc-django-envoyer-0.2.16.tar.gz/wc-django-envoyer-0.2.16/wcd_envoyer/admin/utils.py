from typing import *
import json

from django.forms import BaseInlineFormSet
from django.forms.formsets import DELETION_FIELD_NAME
from django.utils.html import mark_safe
from django.utils.translation import pgettext_lazy

from wcd_envoyer.shortcuts import get_backend


__all__ = (
    'EntangledFormSet',
    'FormAdminMixin', 'JsonDataAdminMixin',
    'prettify_json', 'render_html_table',
)


class EntangledFormSet(BaseInlineFormSet):
    def add_fields(self, form, index):
        super().add_fields(form, index)

        if self.can_delete:
            form._meta.untangled_fields.append(DELETION_FIELD_NAME)


class FormAdminMixin:
    add_form = None
    add_fieldsets = None
    add_inlines = None

    def get_backend_form_class(self, request, obj, backend):
        raise NotImplementedError()

    def get_form(self, request, obj=None, **kwargs):
        form = None

        if obj is None and self.add_form is not None:
            form = self.add_form

        if obj is not None:
            backend = get_backend(obj.channel)

            if backend is not None:
                form = self.get_backend_form_class(request, obj, backend)

        if form is not None:
            kwargs['form'] = form

        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        self.inlines = self.__class__.inlines

        if obj is None and self.add_inlines is not None:
            self.inlines = self.add_inlines

        if obj is None and self.add_fieldsets is not None:
            return self.add_fieldsets

        return super().get_fieldsets(request, obj)


class JsonDataAdminMixin:
    def json_data(self, obj):
        return mark_safe(prettify_json(getattr(obj, 'data', {})))
    json_data.short_description = pgettext_lazy('wcd_envoyer', 'Json data')


def render_html_table(data: List[Tuple]) -> str:
    html = '<table style="border: 1px solid #ecf2f6;"><tbody>'
    for line in data:
        html += '<tr><td>'
        html += '</td><td>'.join(line)
        html += '</td></tr>'
    html += '</tbody></table>'
    return html


def prettify_json(data: Dict) -> str:
    return ''.join([
        '<span style="white-space: pre-wrap; font-family: monospace">',
            json.dumps(data, ensure_ascii=False, indent=4),
        '</span>',
    ])
