import pytest

from zoneinfo import ZoneInfo
import datetime
from celery import Celery

from wcd_envoyer.contrib.scheduled.shortcuts import task, make_task, make_scheduled_task
from wcd_envoyer.models import ChannelConfig, Message
from wcd_envoyer.contrib.scheduled.models import (
    EventAvailability, ChannelAvailability, MessageSchedule
)

from .const import CONSOLE_CHANNEL
from .utils import make_template


EVENT_ONE = 'unexisting_event'


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
    runner_task = make_task(app)
    return runner_task.send, runner_task, app


@pytest.mark.django_db
def test_unscheduled_celery_send(django_assert_num_queries, simple_console_config, mocker):
    send, _, _ = make_send()

    with django_assert_num_queries(13):
        mocker.patch(
            'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
            lambda self, config, messages, context: (messages, []),
        )
        send(
            EVENT_ONE,
            [{'user_id': 1}, {'user_id': 2}],
            {'username': 'Named', 'language': 'ja'},
        )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.SENT).count() == 2



@pytest.mark.django_db
def test_scheduled_celery_send(django_assert_num_queries, simple_console_config, mocker):
    send, _, _ = make_send()
    *_, config = simple_console_config
    UTC = ZoneInfo('UTC')
    now = datetime.datetime(2025, 1, 1, 1, 0, 0, 0, tzinfo=UTC)
    EventAvailability.objects.bulk_create([
        EventAvailability(
            events=[EVENT_ONE],
            available_since=datetime.time(2, 0, 0),
            available_till=datetime.time(5, 0, 0),
        ),
    ])

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [{'user_id': 1}, {'user_id': 2}],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.SENT).count() == 0
    assert Message.objects.filter(status=Message.Status.NEW).count() == 2
    assert MessageSchedule.objects.count() == 2
    assert MessageSchedule.objects.filter(send_at=now.replace(hour=2)).count() == 2


@pytest.mark.django_db
def test_intersecting_time_send(django_assert_num_queries, simple_console_config, mocker):
    send, _, _ = make_send()
    *_, config = simple_console_config
    UTC = ZoneInfo('UTC')
    now = datetime.datetime(2025, 1, 1, 1, 0, 0, 0, tzinfo=UTC)
    ChannelAvailability.objects.bulk_create([
        ChannelAvailability(
            config=config,
            available_since=datetime.time(1, 30, 0),
            available_till=datetime.time(2, 0, 0),
        ),
        ChannelAvailability(
            config=config,
            available_since=datetime.time(4, 30, 0),
            available_till=datetime.time(6, 0, 0),
        ),
    ])
    EventAvailability.objects.bulk_create([
        EventAvailability(
            events=[EVENT_ONE],
            available_since=datetime.time(2, 0, 0),
            available_till=datetime.time(4, 0, 0),
        ),
        EventAvailability(
            events=[EVENT_ONE],
            available_since=datetime.time(3, 0, 0),
            available_till=datetime.time(5, 0, 0),
        ),
    ])

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [{'user_id': 1}, {'user_id': 2}],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.SENT).count() == 0
    assert Message.objects.filter(status=Message.Status.NEW).count() == 2
    assert MessageSchedule.objects.count() == 2
    assert MessageSchedule.objects.filter(send_at=now.replace(hour=2)).count() == 2


@pytest.mark.django_db
def test_send_tomorrow_because_late(django_assert_num_queries, simple_console_config, mocker):
    send, _, _ = make_send()
    *_, config = simple_console_config
    UTC = ZoneInfo('UTC')
    now = datetime.datetime(2025, 1, 1, 16, 0, 0, 0, tzinfo=UTC)
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

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [{'user_id': 1}, {'user_id': 2}],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.SENT).count() == 0
    assert Message.objects.filter(status=Message.Status.NEW).count() == 2
    assert MessageSchedule.objects.count() == 2
    assert MessageSchedule.objects.filter(send_at=now.replace(day=2, hour=2)).count() == 2


@pytest.mark.django_db
def test_send_other_timezone(django_assert_num_queries, simple_console_config, mocker):
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

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [
            {'user_id': 1, 'tz': 'Australia/West'},
            {'user_id': 2},
            {'user_id': 3, 'tz': 'Africa/Algiers'},
        ],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 3
    assert Message.objects.filter(status=Message.Status.SENT).count() == 1
    assert Message.objects.filter(status=Message.Status.NEW).count() == 2
    assert MessageSchedule.objects.count() == 2
    assert MessageSchedule.objects.filter(send_at=now.replace(hour=2)).count() == 1
    assert MessageSchedule.objects.filter(send_at=now.replace(hour=18)).count() == 1


@pytest.mark.django_db
def test_scheduled_task(django_assert_num_queries, simple_console_config, mocker):
    send, t, app = make_send()
    scheduled_task = make_scheduled_task(app, sender=t.sender)

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

    mocker.patch(
        'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
        lambda self, config, messages, context: (messages, []),
    )
    send(
        EVENT_ONE,
        [
            {'user_id': 1, 'tz': 'Australia/West'},
        ],
        {'username': 'Named', 'language': 'ja', 'now': now},
    )

    assert Message.objects.all().count() == 1
    assert Message.objects.filter(status=Message.Status.NEW).count() == 1
    assert MessageSchedule.objects.count() == 1

    scheduled_task.apply_async(kwargs={
        'now': datetime.datetime(2025, 1, 1, 18, 0, 59, 0, tzinfo=UTC),
        'delta_seconds': datetime.timedelta(minutes=1).total_seconds(),
    })

    assert MessageSchedule.objects.count() == 0
    assert Message.objects.filter(status=Message.Status.NEW).count() == 0
    assert Message.objects.filter(status=Message.Status.SENT).count() == 1
