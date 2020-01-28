from django import template

from strikecircle.models import Pledge

register = template.Library()

@register.filter
def index(value, arg):
    try:
        val = value[arg]
    except KeyError:
        val = None

    return val
