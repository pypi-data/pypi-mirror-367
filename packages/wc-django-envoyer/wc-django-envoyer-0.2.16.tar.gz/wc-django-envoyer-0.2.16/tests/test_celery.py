import pytest

from celery import Celery

from wcd_envoyer.contrib.celery.shortcuts import task, make_task
from wcd_envoyer.models import ChannelConfig, Message

from .const import CONSOLE_CHANNEL
from .utils import make_template


EVENT_ONE = 'unexisting_event'


@pytest.fixture
@pytest.mark.django_db
def simple_console_config():
    config = ChannelConfig.objects.create(channel=CONSOLE_CHANNEL)

    return *make_template(CONSOLE_CHANNEL, EVENT_ONE), config


@pytest.mark.django_db
def test_celery_send(django_assert_num_queries, simple_console_config, mocker):
    app = Celery('app')
    app.conf.update(
        task_always_eager=True,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
    runner_task = make_task(app)
    send = runner_task.send

    with django_assert_num_queries(9):
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
def test_celery_callback(django_assert_num_queries, simple_console_config, mocker):
    app = Celery('app')
    app.conf.update(
        task_always_eager=True,
        broker_url='memory://',
        result_backend='cache+memory://',
    )
    saved = {}

    @task(app)
    def runner_task(result, context):
        saved['succeeded'], saved['failed'] = result

    send = runner_task.send

    with django_assert_num_queries(9):
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
    assert len(saved) == 2
