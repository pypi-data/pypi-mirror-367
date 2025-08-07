from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = 'ScheduledEnvoyerConfig',


class ScheduledEnvoyerConfig(AppConfig):
    name = 'wcd_envoyer.contrib.scheduled'
    label = 'wcd_envoyer_scheduled'
    verbose_name = pgettext_lazy('wcd_envoyer', 'Envoyer: Scheduled')
