from django import template

register = template.Library()

@register.filter
def dot_decimal(value):
    """Virgülleri noktaya çevirir"""
    if value is None:
        return ""
    return str(value).replace(",", ".")
