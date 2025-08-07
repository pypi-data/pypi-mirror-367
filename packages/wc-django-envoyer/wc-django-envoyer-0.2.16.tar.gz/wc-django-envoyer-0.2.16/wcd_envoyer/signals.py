from django.dispatch import Signal


messages_sent = Signal()
messages_sent_succeeded = Signal()
messages_sent_failed = Signal()
