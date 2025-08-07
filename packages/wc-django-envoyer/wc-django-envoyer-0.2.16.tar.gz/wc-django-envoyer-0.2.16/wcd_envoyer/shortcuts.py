from typing import *

from .services.sender import Sender
from .channels import MessageData, Recipients, BaseMessagingBackend


__all__ = 'default_sender', 'send_multiple', 'send', 'get_backend',


default_sender = Sender()
send_multiple = default_sender.send


def send(
    event: str,
    recipients: Recipients,
    context: dict,
    channels: Optional[Sequence[str]] = None,
    sender: Sender = default_sender,
):
    all_channels = (
        channels
        if channels is not None else
        sender.get_backends().keys()
    )

    return sender.send(
        [
            MessageData(channel, event, recipients, context)
            for channel in all_channels
        ],
        context=context,
        only_channels=channels,
    )


def get_backend(
    channel: str,
    sender: Sender = default_sender,
) -> Optional[BaseMessagingBackend]:
    return sender.get_backends(only_channels=[channel]).get(channel, None)
