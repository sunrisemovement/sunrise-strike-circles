from django import template

register = template.Library()

@register.filter
def index(value, arg):
    return value[arg]
