from django import template

register = template.Library()

@register.filter
def dot_decimal(value):
    """Virgülleri noktaya çevirir"""
    if value is None:
        return ""
    return str(value).replace(",", ".")

@register.filter
def get_item(dictionary, key):
    """Güvenli dict.get kullanımı"""
    try:
        if dictionary is None:
            return None
        return dictionary.get(key)
    except Exception:
        return None