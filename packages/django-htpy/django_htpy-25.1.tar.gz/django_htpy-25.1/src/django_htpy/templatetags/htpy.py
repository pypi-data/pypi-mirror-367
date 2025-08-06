from django import template
from django.utils.module_loading import import_string


register = template.Library()


@register.simple_tag
def htpy(component_path, *args, **kwargs):
    component = import_string(component_path)
    return component(*args, **kwargs)
