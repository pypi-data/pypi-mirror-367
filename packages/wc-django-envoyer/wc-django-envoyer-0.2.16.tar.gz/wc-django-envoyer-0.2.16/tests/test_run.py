import pytest

from django.test import override_settings
from wcd_envoyer.models import ChannelConfig, Message
from wcd_envoyer.shortcuts import send
from django.core import mail

from .const import CONSOLE_CHANNEL, EMAIL_CHANNEL
from .utils import make_template


EVENT_ONE = 'unexisting_event'


@pytest.fixture
@pytest.mark.django_db
def simple_console_config():
    config = ChannelConfig.objects.create(channel=CONSOLE_CHANNEL)

    return *make_template(CONSOLE_CHANNEL, EVENT_ONE), config


@pytest.fixture
@pytest.mark.django_db
def simple_email_config():
    config = ChannelConfig.objects.create(channel=EMAIL_CHANNEL, data={
        'from_email': 'galina@blanka.bulbul',
        'reply_to': ['John Doe <john@doe.com>', 'bubel@gmail.com'],
    })

    return *make_template(EMAIL_CHANNEL, EVENT_ONE), config


@pytest.mark.django_db
def test_simple_sender(django_assert_num_queries, simple_console_config, mocker):
    with django_assert_num_queries(6):
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
def test_simple_sender_inactive_channel(django_assert_num_queries, simple_console_config, mocker):
    _, _, config = simple_console_config
    config.is_active = False
    config.save()

    with django_assert_num_queries(3):
        mocker.patch(
            'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
            lambda self, config, messages, context: (messages, []),
        )
        send(
            EVENT_ONE,
            [{'user_id': 1}, {'user_id': 2}],
            {'username': 'Named', 'language': 'ja'},
        )

    assert Message.objects.all().count() == 0


@pytest.mark.django_db
def test_succeed_failed_lists(django_assert_num_queries, simple_console_config, mocker):
    with django_assert_num_queries(6):
        mocker.patch(
            'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
            lambda self, config, messages, context: (messages[:1], [(messages[1], None)]),
        )
        send(
            EVENT_ONE,
            [{'user_id': 1}, {'user_id': 2}],
            {'username': 'Named', 'language': 'ja'},
        )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.SENT).count() == 1
    assert Message.objects.filter(status=Message.Status.FAILED).count() == 1


@pytest.mark.django_db
def test_send_exception(django_assert_num_queries, simple_console_config, mocker):
    with django_assert_num_queries(6):
        mocker.patch(
            'wcd_envoyer.channels.backends.console.ConsoleBackend.send',
            lambda self, config, messages, context: (_ for _ in ()).throw(Exception()),
        )
        send(
            EVENT_ONE,
            [{'user_id': 1}, {'user_id': 2}],
            {'username': 'Named', 'language': 'ja'},
        )

    assert Message.objects.all().count() == 2
    assert Message.objects.filter(status=Message.Status.FAILED).count() == 2


@pytest.mark.django_db
def test_inactive_template(django_assert_num_queries, simple_console_config):
    template, _, _ = simple_console_config
    template.is_active = False
    template.save()

    with django_assert_num_queries(2):
        send(
            EVENT_ONE,
            [{'user_id': 1}, {'user_id': 2}],
            {'username': 'Named'},
        )

    assert Message.objects.all().count() == 0


@pytest.mark.django_db
def test_email(django_assert_num_queries, simple_email_config):
    with django_assert_num_queries(6):
        mail.outbox.clear()

        with override_settings(
            EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
        ):
            send(
                EVENT_ONE,
                [{'email': 'ad@ad.ad'}, {'user_id': 2}],
                {'username': 'Named', 'language': 'ja'},
            )

    assert Message.objects.all().count() == 1
    assert Message.objects.filter(status=Message.Status.SENT).count() == 1
    assert len(mail.outbox) == 1

    msg = str(mail.outbox[0].message())

    assert '[ja] NOt a plain. [ja] Hi Named test_email !' in msg
    assert 'From: galina@blanka.bulbul' in msg
    assert 'To: ad@ad.ad' in msg
    assert 'Reply-To: John Doe <john@doe.com>, bubel@gmail.com' in msg
