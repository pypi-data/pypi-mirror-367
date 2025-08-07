from dataclasses import dataclass, field
from typing import *

from px_settings.contrib.django import settings as setting_wrap

from .channels import ChannelInfoType
from .events import EventInfoType
from .const import SETTINGS_PREFIX


__all__ = 'Settings', 'settings',


@setting_wrap(SETTINGS_PREFIX)
@dataclass
class Settings:
    CHANNELS: Sequence[ChannelInfoType] = field(default_factory=list)
    EVENTS: Sequence[EventInfoType] = field(default_factory=list)
    JSON_ENCODER: str = 'wcd_envoyer.utils.types.EnvoyerJSONEncoder'


settings = Settings()
