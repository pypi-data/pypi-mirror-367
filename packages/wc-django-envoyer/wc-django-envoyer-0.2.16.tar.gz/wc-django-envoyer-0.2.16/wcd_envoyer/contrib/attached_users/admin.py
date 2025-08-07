from django.contrib import admin

from .models import MessageAttachedUser


__all__ = 'MessageAttachedUserAdmin',


@admin.register(MessageAttachedUser)
class MessageAttachedUserAdmin(admin.ModelAdmin):
    list_display = 'id', 'message', 'user',
    list_select_related = 'message', 'user',
    autocomplete_fields = 'message', 'user',
