from typing import *
from functools import partial, wraps
from wcd_envoyer.contrib.celery import shortcuts

from .services.sender import ScheduledCelerySender
from .tasks import actual_scheduled_sending_messages_task

if TYPE_CHECKING:
    from celery import Celery


__all__ = 'make_task', 'make_scheduled_task', 'task',


make_task = partial(shortcuts.make_task, sender_class=ScheduledCelerySender)
task = partial(shortcuts.task, sender_class=ScheduledCelerySender)


def make_scheduled_task(
    app: 'Celery',
    sender: ScheduledCelerySender,
    task_kwargs: dict = {},
    task_callback: Optional[Callable] = None,
    **kwargs,
):
    to_wrap = task_callback or actual_scheduled_sending_messages_task
    fn = wraps(to_wrap)(lambda *a, **kw: actual_scheduled_sending_messages_task(
        *a, **{**kwargs, **kw, 'sender': sender, 'callback': task_callback},
    ))
    return app.task(**task_kwargs)(fn)
