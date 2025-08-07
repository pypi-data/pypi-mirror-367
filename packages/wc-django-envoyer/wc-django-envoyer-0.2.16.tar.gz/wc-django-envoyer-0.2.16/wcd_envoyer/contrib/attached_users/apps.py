from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


__all__ = 'AttachedUsersEnvoyerConfig',


class AttachedUsersEnvoyerConfig(AppConfig):
    name = 'wcd_envoyer.contrib.attached_users'
    label = 'wcd_envoyer_attached_users'
    verbose_name = pgettext_lazy('wcd_envoyer', 'Envoyer: Attached users')
