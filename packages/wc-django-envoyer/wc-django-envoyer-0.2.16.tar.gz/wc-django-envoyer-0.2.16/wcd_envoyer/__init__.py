__version__ = '0.2.16'

from django.utils.module_loading import autodiscover_modules

VERSION = tuple(__version__.split('.'))

default_app_config = 'wcd_envoyer.apps.EnvoyerConfig'


def autodiscover():
    from .conf import settings
    from . import channels, events

    autodiscover_modules('envoyer')

    for event in settings.EVENTS:
        events.registry.add(event)

    for channel in settings.CHANNELS:
        channels.registry.add(channel)
