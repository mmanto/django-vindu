from django.conf.urls import url

from .views import *
from .api import *
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^argentina/(?P<external_reference>.+)/ipn/$', ipn_argentina, name='ipn_argentina'),
    url(r'^mercadopago/pago-exitoso/$', mp_pago_exitoso, name='mp_pago_exitoso'),
    url(r'^mercadopago/pago-erroneo/$', TemplateView.as_view(template_name='pagos/mp_pago_erroneo.html'), name='mp_pago_erroneo'),
    url(r'^mercadopago/pago-pendiente/$', TemplateView.as_view(template_name='pagos/mp_pago_pendiente.html'), name='mp_pago_pendiente'),
    url(r'^mercadopago/pago-rechazado/$', TemplateView.as_view(template_name='pagos/mp_pago_rechazado.html'), name='mp_pago_rechazado'),
    url(r'^prueba_mail_html/$', prueba_mail_html, name='prueba_mail_compra'),
]
'''
url(r'^mercadopago/pago-exitoso/$', MP_PagoExitosoViewSet.as_view({'get': 'list'}), name='mp-pago-exitoso'),
url(r'^mercadopago/pago-erroneo/$', MP_PagoErroneoViewSet.as_view({'get': 'list'}), name='mp-pago-erroneo'),
url(r'^mercadopago/pago-pendiente/$', MP_PagoPendienteViewSet.as_view({'get': 'list'}), name='mp-pago-pendiente'),
url(r'^mercadopago/pago-rechazado/$', MP_PagoRechazadoViewSet.as_view({'get': 'list'}), name='mp-pago-rechazado'),
url(r'^prueba_mail_html/$', prueba_mail_html, name='prueba_mail_compra'),
'''