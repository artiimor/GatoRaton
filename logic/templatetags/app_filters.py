from django import template
register = template.Library()

@register.filter('get_value')
def get_value(dict_data, key):
    if key:
        ret = dict_data.get(key)
    return ret

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)

@register.filter
def index(indexable, i):
    return indexable[i]
