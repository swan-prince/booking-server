from django import template
from django.urls import reverse, NoReverseMatch

import re

register = template.Library()


@register.simple_tag(takes_context=True)
def is_active_class(context, pattern_or_urlname):
    try:
        pattern = '^' + reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname
    path = context['request'].path
    if re.search(pattern, path):
        return 'active'
    return ''


@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    params = context['request'].GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    for k in [k for k, v in params.items() if not v]:
        del params[k]
    return params.urlencode()


@register.filter
def pathfor(service_slug, category=None):
    if category:
        return '/' + category + '/' + service_slug + '/'
    return '/seller/' + service_slug + '/'


@register.filter
def booking(booking_status):
    if booking_status == 'booked':
        return 'text-success'
    elif booking_status == 'canceled':
        return 'text-danger'
    elif booking_status == 'expired':
        return 'text-warning'
    else:
        return 'text-secondary'