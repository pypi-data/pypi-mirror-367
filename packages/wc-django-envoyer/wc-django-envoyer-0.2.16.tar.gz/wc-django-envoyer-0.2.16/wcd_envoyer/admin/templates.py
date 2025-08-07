from django.contrib import admin
from django.utils.html import mark_safe
from django.utils.translation import pgettext_lazy, pgettext

from pxd_lingua.admin import TranslationsInlineAdmin

from wcd_envoyer import events
from wcd_envoyer.channels.forms import BaseTemplateForm
from wcd_envoyer.models import Template, TemplateTranslation
from wcd_envoyer.shortcuts import get_backend

from .forms import AddTemplateForm
from .utils import (
    EntangledFormSet, FormAdminMixin, JsonDataAdminMixin, render_html_table
)


__all__ = 'TemplateTranslationsInlineAdmin', 'TemplateAdmin',


class TemplateTranslationsInlineAdmin(TranslationsInlineAdmin):
    formset = EntangledFormSet
    model = TemplateTranslation

    def get_ent_form(self, parent_obj):
        backend = get_backend(parent_obj.channel)

        BaseForm = (
            BaseTemplateForm
            if backend is None else
            backend.template_form_class
        )

        trans_untangled_fields = [
            field for field in getattr(BaseForm.Meta, 'untangled_fields', [])
            if field not in {'channel', 'event', 'is_active'}
        ] + ['language']

        class TransForm(BaseForm, self.form):
            class Meta(BaseForm.Meta):
                fields = 'language',
                model = self.model
                untangled_fields = trans_untangled_fields

        return TransForm

    def get_formset(self, request, obj=None, **kwargs):
        self.form = self.__class__.form

        if obj:
            if not hasattr(self, '_ent_form'):
                self._ent_form = self.get_ent_form(obj)
            self.form = self._ent_form or self.form
        return super().get_formset(request, obj=obj, **kwargs)


@admin.register(Template)
class TemplateAdmin(JsonDataAdminMixin, FormAdminMixin, admin.ModelAdmin):
    add_form = AddTemplateForm
    add_fieldsets = (None, {'fields': ['channel', 'event']}),
    add_inlines = ()
    inlines = TemplateTranslationsInlineAdmin,
    list_display = 'channel', 'event', 'is_active', 'created_at', 'updated_at',
    list_filter = 'channel', 'event', 'is_active',
    date_hierarchy = 'created_at'
    readonly_fields = 'legend', 'json_data',
    search_fields = 'channel', 'event', 'data', 'status',

    def get_backend_form_class(self, request, obj, backend):
        return backend.template_form_class

    def wrap_template_key(self, key):
        front, back = '{{ ', ' }}'
        return f'{front}{key}{back}'

    def legend(self, obj):
        if not getattr(obj, 'pk', None):
            return '-'

        event = events.registry.get(obj.event)

        if event is None:
            return '-'

        data = [(
            pgettext('wcd_envoyer', 'Key'),
            pgettext('wcd_envoyer', 'Template key'),
            pgettext('wcd_envoyer', 'Title'),
            pgettext('wcd_envoyer', 'Description'),
        )] + [
            (key, self.wrap_template_key(key), str(title), str(description))
            for key, title, description in event.context
        ]

        return mark_safe(render_html_table(data))
    legend.short_description = pgettext_lazy('wcd_envoyer', 'Legend')
