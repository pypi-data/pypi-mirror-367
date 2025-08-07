from typing import *
import json

from px_domains import Domain
from wcd_envoyer.services.sender import FailedMessagesGroup
from wcd_envoyer.models import Message
from wcd_envoyer.utils import get_json_encoder
from pxd_actions_tracker.cases import log


MESSAGE_FORMAT = 'Failed send "{message[event]}" through "{message[channel]}"'.format


def format_error(error: Union[Exception, dict, str]):
    if isinstance(error, Exception):
        return {'exception': str(error)}

    # FIXME!
    return json.loads(json.dumps(error, cls=get_json_encoder()))


def resolve_log_detail(message: Message, error):
    return {
        'message': {
            'channel': message.channel,
            'event': message.event,
            'recipients': message.recipients,
            'data': message.data,
        },
        'error': format_error(error),
    }


def track_failed_messages_groups(
    domain: Domain,
    groups: Sequence[FailedMessagesGroup],
    message_format: Callable = MESSAGE_FORMAT,
    detail_resolver: Callable = resolve_log_detail,
):
    for backend, config, messages in groups:
        for message, error in messages:
            detail = detail_resolver(message, error)
            log(domain, message=message_format(**detail), detail=detail)
