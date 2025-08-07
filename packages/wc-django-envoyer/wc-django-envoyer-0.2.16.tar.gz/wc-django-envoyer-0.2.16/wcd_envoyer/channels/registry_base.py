from typing import *
from dataclasses import dataclass, field

from .backend import BaseMessagingBackend
from ..utils import EntryRegistry, cached_import_string


__all__ = 'ChannelInfoType', 'ChannelDescriptor', 'ChannelRegistry',


class ChannelInfoType(TypedDict):
    key: str
    verbose_name: Optional[str]
    backend: Union[str, Type[BaseMessagingBackend]]
    options: Optional[dict]


@dataclass
class ChannelDescriptor:
    key: str
    verbose_name: str
    backend: BaseMessagingBackend

    @classmethod
    def from_info(cls, entry: ChannelInfoType):
        key = entry['key']
        verbose_name = entry.get('verbose_name', None) or key.title()
        backend = entry['backend']
        backend = (
            cached_import_string(backend)
            if isinstance(backend, str) else
            backend
        )

        return cls(
            key=key,
            verbose_name=verbose_name,
            backend=backend(**entry.get('options', {})),
        )


class ChannelRegistry(EntryRegistry):
    def transform_input(self, entry: ChannelInfoType):
        return entry['key'], ChannelDescriptor.from_info(entry)

    def get_choices(self):
        return [(key, x.verbose_name) for key, x in self.items()]
