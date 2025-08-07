from django.contrib import admin

from wcd_envoyer.models import ChannelConfig

from .forms import AddConfigForm
from .utils import FormAdminMixin, JsonDataAdminMixin


__all__ = 'ChannelConfigAdmin',


@admin.register(ChannelConfig)
class ChannelConfigAdmin(JsonDataAdminMixin, FormAdminMixin, admin.ModelAdmin):
    add_form = AddConfigForm
    readonly_fields = 'json_data', 'created_at', 'updated_at'

    def get_backend_form_class(self, request, obj, backend):
        return backend.config_form_class
