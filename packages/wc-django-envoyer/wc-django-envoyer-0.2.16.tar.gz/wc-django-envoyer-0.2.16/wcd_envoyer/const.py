from django.utils.translation import pgettext_lazy
from wcd_notifications.compat import TextChoices


__all__ = 'SETTINGS_PREFIX', 'LETTER_STATUSES',

SETTINGS_PREFIX = 'WCD_ENVOYER'


class MessageStatus(TextChoices):
    NEW = '010-new', pgettext_lazy('wcd_envoyer', 'New')
    PENDING = '030-pending', pgettext_lazy('wcd_envoyer', 'Pending')
    SENT = '060-sent', pgettext_lazy('wcd_envoyer', 'Sent')
    FAILED = '080-failed', pgettext_lazy('wcd_envoyer', 'Failed')
