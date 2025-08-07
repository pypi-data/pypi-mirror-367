from typing import *
from pprint import pprint

from wcd_envoyer.models import Message, ChannelConfig

from ..backend import BaseMessagingBackend


def print_heading(message, l=80, s='='):
    print((message + ' ' + (s*l)).strip()[:l])


class ConsoleBackend(BaseMessagingBackend):
    def send(self, config: ChannelConfig, messages: Sequence[Message], context={}):
        print_heading('Printing %s messages' % len(messages))

        for message in messages:
            print_heading('', s='-')
            print('ID: %s' % message.pk)
            print('Channel: %s' % message.channel)
            print('Event: %s' % message.event)
            print('Status: %s' % message.status)
            print('To:')
            pprint(message.recipients, compact=True, indent=2)
            print('Data:')
            pprint(message.data, compact=True, indent=2)
            print_heading('', s='-')

        print_heading('')

        return messages, []
