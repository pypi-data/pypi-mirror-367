# WebCase message sender

Message sender to different channels.

## Installation

```sh
pip install wc-django-envoyer
```

In `settings.py`:

```python
INSTALLED_APPS += [
  'wcd_envoyer',
]

WCD_ENVOYER = {
  # Channels list, that will be available in admin interface to message
  # create templates.
  'CHANNELS': [
    {
      # Unique channel key.
      'key': 'console',
      'verbose_name': 'Console',
      # Messaging backend class.
      # Console backend here is a simple message printing backend:
      'backend': 'wcd_envoyer.channels.backends.console.ConsoleBackend',
      'options': {
        # Options that backend receives on initialization.
        # Basic ones are:
        # Actual recipients data resolver for a specific case:
        'recipient_resolver': lambda x: x,
        # Form for additional in-admin backend configuration options.
        'config_form_class': 'wcd_envoyer.channels.forms.BaseConfigForm',
        # In-admin form for template config.
        'template_form_class': 'wcd_envoyer.channels.forms.BaseTemplateForm',
        # Custom string template renderer.
        'template_renderer': 'wcd_envoyer.channels.renderers.django_template_renderer',
        # Separate class that is responsible for messages data transformations.
        'messages_maker_class': 'wcd_envoyer.channels.backend.MessagesMaker',
      }
    },
  ],
  'EVENTS': [
    {
      # Unique event key.
      'key': 'something-happened',
      # Event's verbose name that will be displayed in admin.
      'verbose_name': 'Something happened event',
      # List of variables available on template generation.
      'context': [
        (
          # Key
          'when',
          # Verbose name.
          'When',
          # Additional variable description
          'Time when something happened.'
        ),
        # Variable can be defined as a simple string key:
        'what',
        # Or this could be tuple with only 2 parameters
        ('other', 'Other'),
      ],
  }
  ],
  # JSON encoder class for in-lib postgres json fields:
  'JSON_ENCODER': 'django.core.serializers.json.DjangoJSONEncoder',
}
```

**Builtin backends:**

- `wcd_envoyer.channels.backends.console.ConsoleBackend` - Simple backend to send messages to console. For debug purposes.
- `wcd_envoyer.channels.backends.django_sendmail.SendMailBackend` - Backend with django's email sending mechanics underneath.

Events and Channels can be registered in special auto-importable `envoyer.py` app submodule.

`envoyer.py`
```python
from django.utils.translation import pgettext_lazy

from wcd_envoyer import events, channels


# Events is better to register here. Because it's more related to
# particular app, not project itself.
events.registry.add({
  'key': 'app-event',
  'verbose_name': 'App event',
  'context': ['var1', 'var2'],
})

# But channels is other case. Better describe them in `settings.py`
channels.registry.add({
  'key': 'sms',
  'verbose_name': 'Sms sender',
  'backend': 'app.envoyer.backends.SMSBackend',
})
```

## Usage

Simple shortcut usage is `send` shortcut.

```python
from wcd_envoyer.shortcuts import send, default_sender

send(
  # Event name
  'app-event',
  # Recipients list.
  # Recipient object is a dict with any key-values, from which different
  # backends will get data they need.
  [
    # This recipient will be used only by sms, or phone call backend.
    {'phone': '+0000000000'},
    # This will be user by email sending backend.
    {'email': 'some@email.com'},
    # And both backends will send message to recipient like that.
    {'phone': '+0000000000', 'email': 'some@email.com'},
  ],
  # Data object, what will be used to render Message.
  # It could be dict with any data.
  # For event probably there will be data for event's context.
  {
    'var1': 'data',
    'var2': 'data',
    # If you need to send messages with specific language, you may add it here:
    'language': 'en',
    # And also any other backend-specific options could be passed to context.
    # ...
  },
  # You may additionally limit channels that message will be send.
  channels=['sms'],
  # Or. None - all channels possible.
  channels=None,
  # Optional parameter, with which you may change sender instance, to your
  # custom one.
  sender=default_sender,
)
```

### Signals

App has internal signals, that you may use to take actions after messages were sended.

- `wcd_envoyer.signals.messages_sent` - Messages sent signal.
- `wcd_envoyer.signals.messages_sent_succeeded` - Signal for messages that were successfully sent.
- `wcd_envoyer.signals.messages_sent_failed` - Signal that fires if any messages were failed to send.

### Celery

Celery support is provided via `wcd_envoyer.contrib.celery` package.

`tasks.py`
```python
from .celery import app

from wcd_envoyer.contrib.celery.shortcuts import task, make_task
from wcd_envoyer.shortcuts import send


# Decorator for task creation is the easiest way to make things work.
@task(app)
def sending_task_1(result, context):
  # Callback for task will run AFTER all messages sending happened.
  succeeded, failed = result
  # - succeeded - List of successfully sent messages.
  # - failed - List of messages that we failed to send.
  # And context - is the same context that were passed on `send`.

# OR

# If you do not need any callback and default signals is enough then just
# create task:
sending_task_2 = make_task(app)

created_task = (sending_task_1 or sending_task2)

# An now, after you've created task and sender you may easily send messages:
send(
  'app-event', [{'email': 'some@email.com'}], {'var': 'data'},
  # You may use sender in initial shortcut:
  sender=created_task.sender,
)
# OR
# Execute the same `send` from task:
created_task.send(
  'app-event', [{'email': 'some@email.com'}], {'var': 'data'},
)
# OR
# Just use created sender directly:
created_task.sender.send(...)
```

To use celery sender in admin interface instead of the "straight" one you should change sender in `Message` admin class:

```python
from wcd_envoyer.admin import MessageAdmin

# Looking hacky, but you you need - just inherit from `MessageAdmin`
# and re-register admin for `Message` model.
MessageAdmin.messages_sender = created_task.sender
```

### Error tracking

You can track failed messages with signals. Or there is a simple connector for `px-django-actions-tracker` lib. Just add `'wcd_envoyer.contrib.pxd_actions_tracker'` to `INSTALLED_APPS`.


### Scheduled message sender

There is an more complex Celery sender, that adds an ability to configure the time of day when the messages could be sent to user. Because we do not want to send messages like "New article added" near midnight, because people are tend to sleep at that time.

There are only small changes required to enable the control.

Add `wcd_envoyer.contrib.scheduled` near the `wcd_envoyer.contrib.celery` package in the `INSTALLED_APPS` django configuration.

```python
# Instead of:
from wcd_envoyer.contrib.celery.shortcuts import task, make_task
# Import task generator from `scheduled` app:
from wcd_envoyer.contrib.scheduled.shortcuts import (
  task, make_task, make_scheduled_task,
)

# Made new task as before:
celery_send_task = make_task(app)
celery_sender = celery_send_task.sender
send = celery_send_task.send

# And add another task, that you will run from time to time using Celery beat
# or crontab or anyway else you want.
# It will send the messages that were scheduled before.
celery_scheduled_send_task = make_scheduled_task(app, sender=celery_sender)
```

#### Configuration

You may configure availability time ranges:
- For every event: `/admin/wcd_envoyer_scheduled/eventavailability/`.
- For every channel configuration: `/admin/wcd_envoyer/channelconfig/`.

If configured both -  message will be send only at the intersecting time.

If, for whatever reason, you've configured that there is not intersection for a pair of channel+event availability ranges - then messages will be sent immediately.

#### Sending

In terms of sending there is not much that have changed.
You may "send" messages just as before, so all of your old code could stay the same.

```python
send(
  'app-event', [{'email': 'some@email.com'}], {'var': 'data'},
)
```

Or, with an additional configuration:
```python
send(
  'app-event',
  [
    {
      'email': 'some@email.com',
      # If there is a timezone passed to a recipient data - message send time
      # will be adjusted to fit it.
      'tz': 'Europe/Berlin',
      # If for this particular recipient message must be sent right now -
      # `send_immediate` key must be set as True:
      'send_immediate': True,
    }
  ],
  {
    'var': 'data',
    # If all the messages must be sent immediately, no matter the
    # configurations you may pass `send_immediate` configuration here:
    'send_immediate': True,
    # Also if for some reason you need to change the current time, based on
    # which library will calculate messages send time you may add `now` to
    # context.
    # By default django's built in `django.utils.timezone.now` will be used.
    'now': timezone.now(),
  },
)
```

All the keys like `tz`, `now`, `immediate` and all possible others are configurable in a `Sender` class. So you may extend the default one and override those parameters.


### User "attachment"

By default `recipients` in library have no connections to django's auth system. But in most scenarios it, in fact, will be. So for that case there is an addon `wcd_envoyer.contrib.attached_users`, that must be added to `INSTALLED_APPS` config.

After that it you may extend your currently used `Sender` with `wcd_envoyer.contrib.attached_users.services.sender.AttachedUserSenderMixin` mixin.

```python
from wcd_envoyer.contrib.attached_users.services.sender import AttachedUserSenderMixin


class MySender(AttachedUserSenderMixin, OldSender):
  pass
```

Now, to attach users to messages simply add `'user_id': user.pk` to the recipient on send:

```python
send(
  'app-event',
  [
    {
      'email': user.email,
      # `user_id` key may be changed in `MySender.USER_ID_KEY` attribute.
      'user_id': user.pk,
    }
  ],
  {'var': 'data'},
)
```
