from typing import *
from datetime import datetime
from collections import defaultdict
from django.contrib.auth import get_user_model

from django.utils import timezone
from django.db.models import prefetch_related_objects

from wcd_envoyer.channels.backend import BaseMessagingBackend
from wcd_envoyer.services.sender import TemplatedMessagesGroup, TemplatedMessages
from wcd_envoyer.models import ChannelConfig, Message
from wcd_envoyer.contrib.celery.services.sender import CelerySender
from wcd_envoyer.channels import MessageData

from ..models import MessageAttachedUser


__all__ = 'AttachedUserSenderMixin',


class AttachedUserSenderMixin:
    USER_ID_KEY: str = 'user_id'
    ATTACHED_USERS_KEY: str = 'attached_user_identifiers'

    def inject_user_ids_to_context(self, items: TemplatedMessages):
        user_id_key = self.USER_ID_KEY
        users_key = self.ATTACHED_USERS_KEY

        for message, _ in items:
            user_identifiers = {
                recipient.get(user_id_key)
                for recipient in message.recipients
            } - {None}

            if len(user_identifiers) == 0:
                continue

            message.context = {
                **message.context, users_key: list(user_identifiers),
            }

        return items

    def attach_users(self, messages: Iterable[Message]):
        attaches = []
        users_key = self.ATTACHED_USERS_KEY

        for message in messages:
            for user_id in message.data.get(users_key, []):
                attaches.append(MessageAttachedUser(
                    message_id=message.pk, user_id=user_id,
                ))

        existing_users = set(
            get_user_model().objects
            .filter(pk__in=[x.user_id for x in attaches])
            .values_list('pk', flat=True)
        )

        MessageAttachedUser.objects.bulk_create(
            [x for x in attaches if x.user_id in existing_users],
            ignore_conflicts=True,
        )

        return attaches

    def make_backend_messages(
        self,
        backend: BaseMessagingBackend,
        config: ChannelConfig,
        items: TemplatedMessages,
        context: dict = {},
    ) -> List[Message]:
        return backend.make_messages(
            config, self.inject_user_ids_to_context(items), context=context,
        )

    def make_messages(
        self,
        templated_messages: Iterable[TemplatedMessagesGroup],
        context: dict = {},
    ) -> List[Tuple[BaseMessagingBackend, ChannelConfig, List[Message]]]:
        result = super().make_messages(templated_messages, context=context)

        self.attach_users((y for _, _, x in result for y in x))

        return result
