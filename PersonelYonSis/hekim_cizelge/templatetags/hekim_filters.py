from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """
    Splits a string by the specified delimiter
    Usage: {{ value|split:"," }}
    """
    return value.split(arg)

@register.filter(name='filter_by_name')
def filter_by_name(hizmetler, hizmet_name):
    """Hizmet listesinden isimle eşleşen hizmeti bulur"""
    for hizmet in hizmetler:
        if hizmet.HizmetName.strip() == hizmet_name.strip():
            return hizmet
    return None

@register.filter
def get_item(dictionary, key):
    """Dictionary'den key ile değer alma filter'ı"""
    return dictionary.get(key)
