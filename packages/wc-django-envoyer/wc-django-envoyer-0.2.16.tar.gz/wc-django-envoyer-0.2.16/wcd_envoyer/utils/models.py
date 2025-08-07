from typing import *
from functools import partialmethod

from django.db import models


__all__ = (
    'DynamicChoicesField',
)


class DynamicChoicesField(models.CharField):
    _choices_resolver: Callable

    @property
    def choices(self):
        result = self._choices_resolver()
        return result if isinstance(result, list) else list(result)

    @choices.setter
    def choices(self, value: Callable):
        if isinstance(value, (list, tuple)):
            saved = value
            def value(): return saved

        self._choices_resolver = value

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["choices"] = []
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        super().contribute_to_class(cls, name, private_only=private_only)

        mname = 'get_%s_display' % self.name

        if not hasattr(cls, mname):
            setattr(cls, mname, partialmethod(cls._get_FIELD_display, field=self))
