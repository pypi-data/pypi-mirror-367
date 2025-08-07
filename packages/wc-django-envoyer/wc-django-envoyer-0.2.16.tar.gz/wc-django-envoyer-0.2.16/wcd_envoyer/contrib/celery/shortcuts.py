from typing import *
from functools import partial, wraps

from wcd_envoyer.shortcuts import send

from .services.sender import CelerySender
from .tasks import actual_sending_messages_task

if TYPE_CHECKING:
    from celery import Celery


__all__ = 'make_task', 'task',


def make_task(
    app: 'Celery',
    apply_kwargs: dict = {},
    task_kwargs: dict = {},
    sender_class: Type[CelerySender] = CelerySender,
    task_callback: Optional[Callable] = None,

    **kwargs,
):
    sender = sender_class(
        celery_task_caller=lambda *a, **kw: task.apply_async(
            args=a, kwargs=kw, **apply_kwargs
        ),
        **kwargs,
    )
    to_wrap = task_callback or actual_sending_messages_task
    fn = wraps(to_wrap)(lambda *a, **kw: actual_sending_messages_task(
        *a, **kw, sender=sender, callback=task_callback,
    ))

    task = app.task(**task_kwargs)(fn)
    task.sender = sender
    task.send = partial(send, sender=sender)

    return task


def task(
    app: 'Celery',
    apply_kwargs: dict = {},
    task_kwargs: dict = {},
    **kwargs,
):
    return lambda task_callback: make_task(
        app, apply_kwargs=apply_kwargs, task_kwargs=task_kwargs, **kwargs,
        task_callback=task_callback,
    )
