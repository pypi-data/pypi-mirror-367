from typing import Any

from django.template.backends.django import Template
from django.template.loader import get_template
from htpy import Renderable
from markupsafe import Markup


def dtl(template: Template | str, context: dict[str, Any]) -> Renderable:
    # Resolve template
    if isinstance(template, str):
        template = get_template(template)

    output = template.render(context)
    return Markup(output)
