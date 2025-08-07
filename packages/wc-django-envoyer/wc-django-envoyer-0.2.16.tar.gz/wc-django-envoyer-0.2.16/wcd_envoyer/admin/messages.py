from django.contrib import admin
from django.contrib.messages import INFO

from wcd_envoyer.models import Message
from wcd_envoyer.shortcuts import default_sender
from django.utils.translation import pgettext, pgettext_lazy

from .utils import JsonDataAdminMixin, FormAdminMixin


__all__ = 'MessageAdmin',


@admin.register(Message)
class MessageAdmin(JsonDataAdminMixin, FormAdminMixin, admin.ModelAdmin):
    messages_sender = default_sender
    actions = 'resend_action',
    list_display = 'channel', 'event', 'status', 'created_at', 'updated_at',
    list_filter = 'channel', 'event', 'status',
    readonly_fields = 'json_data', 'created_at', 'updated_at',
    date_hierarchy = 'created_at'
    search_fields = 'channel', 'event', 'recipients', 'data', 'status',

    def get_backend_form_class(self, request, obj, backend):
        BaseForm = backend.template_form_class
        message_untangled_fields = ['status', 'recipients'] + [
            field for field in getattr(BaseForm.Meta, 'untangled_fields', [])
            if field not in {'is_active'}
        ]

        class MessageForm(BaseForm, self.form):
            class Meta(BaseForm.Meta):
                fields = 'channel', 'event', 'recipients', 'data', 'status',
                model = self.model
                untangled_fields = message_untangled_fields

        return MessageForm

    def resend_action(self, request, qs):
        messages = list(qs)
        self.messages_sender.resend(messages)

        self.message_user(
            request=request,
            message=(
                pgettext('wcd_envoyer', 'Resent {} letters.')
                .format(len(messages))
            ),
            level=INFO,
        )
    resend_action.short_description = pgettext_lazy(
        'wcd_envoyer', 'Resend letters',
    )
