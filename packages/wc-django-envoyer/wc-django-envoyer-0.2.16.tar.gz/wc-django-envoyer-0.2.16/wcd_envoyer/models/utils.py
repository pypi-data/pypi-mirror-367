from django.db import models
from django.utils.translation import pgettext_lazy


__all__ = 'DateTimeModel',


class DateTimeModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        pgettext_lazy('wcd_envoyer', 'Created at'), auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        pgettext_lazy('wcd_envoyer', 'Updated at'), auto_now=True,
    )
