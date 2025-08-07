import pytest

from zoneinfo import ZoneInfo
import datetime
from celery import Celery

from django.contrib.auth import get_user_model
from wcd_envoyer.contrib.scheduled.shortcuts import make_task
from wcd_envoyer.contrib.scheduled.services.sender import ScheduledCelerySender
from wcd_envoyer.contrib.attached_users.services.sender import AttachedUserSenderMixin
from wcd_envoyer.models import ChannelConfig, Message
from wcd_envoyer.contrib.attached_users.models import MessageAttachedUser
from wcd_envoyer.contrib.scheduled.models import (
    EventAvailability, ChannelAvailability,
)

from .const import CONSOLE_CHANNEL
from .utils import make_template


EVENT_ONE = 'unexisting_event'


class Sender(AttachedUserSenderMixin, ScheduledCelerySender):
    pass


@pytest.fixture
@pytest.mark.django_db
def simple_console_config():
    config = ChannelConfig.objects.create(channel=CONSOLE_CHANNEL)
    return *make_template(CONSOLE_CHANNEL, EVENT_ONE), config


def make_send():
    app = Celery('app')
    app.conf.update(
        task_always_eager=True,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
    runner_task = make_task(app, sender_class=Sender)
    return runner_task.send, runner_task, app


@pytest.mark.django_db
def test_existing_users_and_not(django_assert_num_queries, simple_console_config, mocker):
    send, _, _ = make_send()
    *_, config = simple_console_config
    UTC = ZoneInfo('UTC')
    now = datetime.datetime(2025, 1, 1, 1, 0, 0, 0, tzinfo=UTC)
    ChannelAvailability.objects.bulk_create([
        ChannelAvailability(
            config=config,
            available_since=datetime.time(1, 30, 0),
            available_till=datetime.time(2, 30, 0),
        ),
    ])
    EventAvailability.objects.bulk_create([
        EventAvailability(
            events=[EVENT_ONE],
            available_since=datetime.time(2, 0, 0),
            available_till=datetime.time(4, 0, 0),
        ),
    ])
    User = get_user_model()
    user = User.objects.create_user('login', 'email@email.com', 'pass')

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [
            {'user_id': user.pk, 'tz': 'Australia/West'},
            {'user_id': 2},
            {'user_id': 3, 'tz': 'Africa/Algiers'},
        ],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 3
    assert Message.objects.filter(status=Message.Status.SENT).count() == 1
    assert Message.objects.filter(status=Message.Status.NEW).count() == 2
    assert MessageAttachedUser.objects.count() == 1
    assert MessageAttachedUser.objects.filter(user_id=user.pk).count() == 1
