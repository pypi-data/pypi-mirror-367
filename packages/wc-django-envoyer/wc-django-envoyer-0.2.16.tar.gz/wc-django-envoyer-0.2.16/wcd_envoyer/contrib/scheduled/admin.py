from django.contrib import admin
from django.contrib.admin.filters import EmptyFieldListFilter
from django.contrib.admin.sites import site as admin_site
from django.utils.translation import pgettext_lazy

from wcd_envoyer.admin import ChannelConfigAdmin, MessageAdmin as MessageAdminInitial
from wcd_envoyer.models import Message

from .models import MessageSchedule, ChannelAvailability, EventAvailability


class ChannelAvailabilityInline(admin.StackedInline):
    model = ChannelAvailability
    extra = 0


ChannelConfigAdmin.inlines = list(ChannelConfigAdmin.inlines) + [
    ChannelAvailabilityInline,
]


@admin.register(EventAvailability)
class EventAvailabilityAdmin(admin.ModelAdmin):
    list_display = 'id', 'events', 'available_since', 'available_till',
    list_editable = 'events', 'available_since', 'available_till',
    list_filter = 'events',


MessageAdminBase = MessageAdminInitial

if admin_site.is_registered(Message):
    MessageAdminBase = admin_site._registry[Message].__class__
    admin_site.unregister(Message)


@admin.register(Message)
class MessageAdmin(MessageAdminBase):
    list_select_related = list(MessageAdminBase.list_select_related or []) + [
        'schedule',
    ]
    list_display = list(MessageAdminBase.list_display) + ['get_schedule_send_at']
    list_filter = list(MessageAdminBase.list_filter) + [
        ('schedule', EmptyFieldListFilter),
    ]

    def get_schedule_send_at(self, obj):
        return obj.schedule.send_at
    get_schedule_send_at.short_description = pgettext_lazy('wcd_envoyer', 'Send at')
    get_schedule_send_at.admin_order_field = 'schedule__send_at'
