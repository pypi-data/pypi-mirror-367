from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = 'ActionsTrackerConfig',


class ActionsTrackerConfig(AppConfig):
    name = 'wcd_envoyer.contrib.pxd_actions_tracker'
    label = 'wcd_envoyer_actions_tracker'
    verbose_name = pgettext_lazy('wcd_envoyer', 'Envoyer actions tracker')

    def ready(self) -> None:
        from . import handlers
