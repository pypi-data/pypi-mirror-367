from typing import *
from dataclasses import dataclass, field

from .utils import EntryRegistry


__all__ = 'EventInfoType', 'EventDescriptor', 'EventRegistry',

ContextKey = Tuple[str, str, str]
ContextKeyInfo = Union[Tuple[str, str], ContextKey, str]


class EventInfoType(TypedDict):
    key: str
    verbose_name: Optional[str]
    context: Sequence[ContextKeyInfo]


def clear_context_key(key: ContextKeyInfo) -> ContextKey:
    if isinstance(key, str):
        return (key, key.title(), '')

    key, verbose_name, help_text, *_ = tuple(key) + ('', '')

    return (key, verbose_name if verbose_name else key.title(), help_text)


@dataclass
class EventDescriptor:
    key: str
    verbose_name: str
    context: List[ContextKey] = field(default_factory=list)

    @classmethod
    def from_info(cls, entry: EventInfoType):
        key = entry['key']
        verbose_name = entry.get('verbose_name', None) or key.title()

        return cls(
            key=key,
            verbose_name=verbose_name,
            context=[
                clear_context_key(key)
                for key in entry.get('context', [])
            ],
        )


class EventRegistry(EntryRegistry):
    def transform_input(self, entry: EventInfoType):
        return entry['key'], EventDescriptor.from_info(entry)

    def get_choices(self):
        return [(key, x.verbose_name) for key, x in self.items()]


registry = EventRegistry()
add = registry.add
