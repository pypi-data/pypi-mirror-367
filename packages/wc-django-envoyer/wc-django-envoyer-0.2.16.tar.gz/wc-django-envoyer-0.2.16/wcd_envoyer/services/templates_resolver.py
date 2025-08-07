from typing import *
from functools import reduce
from operator import or_

from django.db import models

from wcd_envoyer.models import Template
from wcd_envoyer.utils import KwargsInjector


ClientEventPair = Tuple[str, str]
Templates = Dict[ClientEventPair, Template]


class TemplatesResolver(KwargsInjector):
    queryset = (
        Template.objects
        .filter(is_active=True)
        .prefetch_related('translated')
    )

    def get_templates(self, pairs: Iterable[ClientEventPair]) -> Templates:
        items = self.queryset.filter(reduce(or_, (
            models.Q(channel=channel, event=event)
            for channel, event in pairs
        )))

        return {
            (template.channel, template.event): template
            for template in items
        }
