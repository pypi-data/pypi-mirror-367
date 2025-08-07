from typing import Any, Dict

from django.template import Context, Template


__all__ = 'django_template_renderer',


def django_template_renderer(template: str, context: Dict[str, Any]) -> str:
    return Template(template).render(Context(context))
