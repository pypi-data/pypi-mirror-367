from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = 'EnvoyerConfig',


class EnvoyerConfig(AppConfig):
    name = 'wcd_envoyer'
    verbose_name = pgettext_lazy('wcd_envoyer', 'Envoyer')

    def ready(self) -> None:
        super().ready()

        self.module.autodiscover()
