# -*- encoding: utf-8 -*-

from django import template
from django.conf import settings

register = template.Library()


@register.filter
def get_foto_or_null(foto_obj, request):
    protocolo_dominio = 'https://' + settings.DOMAIN
    try:
        url = foto_obj.url
    except:
        return ''
    else:
        photo_url = foto_obj.url
        absolute_uri = request.build_absolute_uri(photo_url)
        print('absolute_uri: ', absolute_uri)
        return absolute_uri


