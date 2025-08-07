from django.dispatch import receiver

from px_domains import Domain
from wcd_envoyer.signals import messages_sent_failed

from .tracker import track_failed_messages_groups


DEFAULT_DOMAIN = Domain('SENDER') | 'ERROR'


@receiver(messages_sent_failed)
def handle_messages_sent_failed(sender, messages_groups, **kwargs):
    track_failed_messages_groups(DEFAULT_DOMAIN, messages_groups)
