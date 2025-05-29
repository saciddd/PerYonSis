from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Eğer dictionary[key] bir dict ise ve 'value' içeriyorsa, value'yu döndür
    item = dictionary.get(key)
    if isinstance(item, dict) and 'value' in item:
        return item['value']
    return '--'

@register.filter
def get_record_id(mesai_data, day):
    # mesai_data içindeki ilgili günün record ID'sini döndür
    if day in mesai_data:
        return mesai_data[day]['id']
    return '' 