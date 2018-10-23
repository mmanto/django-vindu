from .api import *
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView
            
#from rest_framework.routers import DefaultRouter
#router = DefaultRouter()

from .views import DashboardPedidosView

urlpatterns = [
    url(r'^get-carrito', GetCarritoViewSet.as_view({'get': 'list'}), name='get-carrito'),
    url(r'^agregar-articulo', AgregarArticuloViewSet.as_view(), name='carrito-agregar-producto'),
    url(r'^carrito-detail/(?P<articulo_id>\d+)', csrf_exempt(CarritoDetalleViewSet.as_view()), name='carrito-update-delete-line'),
    url(r'^flush-carrito', GetCarritoViewSet.as_view({'put': 'update'}), name='flush-carrito'),
    url(r'^checkout', CheckoutCarritoViewSet.as_view(), name='carrito-checkout'),
    url(r'^get-domicilios', GetDomiciliosViewSet.as_view({'get': 'list'})),
    url(r'^agregar-domicilio', AgregarDomicilioViewSet.as_view({'post': 'create'})),
    url(r'^domicilio-detail/(?P<domicilio_id>\d+)', DomicilioViewSet.as_view({'delete': 'destroy'}), name="borrar_domicilio"),
    url(r'^set-envio/pedido-detail', csrf_exempt(SetDomicilioEnvioViewSet.as_view({'put': 'update'})), name='pedido-update-dom-envio'),
    url(r'^set-envio/datos-adicionales', csrf_exempt(SetDatosAdicionalesEnvioViewSet.as_view({'put': 'update'})), name='pedido-update-adicionales-envio'),
    url(r'^set-facturacion/pedido-detail', csrf_exempt(SetDomicilioFacturacionViewSet.as_view({'put': 'update'})), name='pedido-update-dom-facturacion'),
    url(r'^set-voucher/pedido-detail', csrf_exempt(SetVoucherViewSet.as_view({'put': 'update'})), name='pedido-update-voucher'),
    url(r'^pagar-pedido', PagarPedidoViewSet.as_view({'put': 'update'}), name='pagar-pedido'),
    url(r'^get-pedidos', GetPedidosViewSet.as_view({'get': 'list'}), name='get-pedidos'),
    url(r'^get-detalle-pedido/(?P<nro_pedido>\d+)', DetallePedidoViewSet.as_view({'get': 'list'}), name='get-detalle-pedido'),
    url(r'^$', RedirectView.as_view(url='/carrito/dashboard-pedidos')),
    url(r'^dashboard-pedidos/$', DashboardPedidosView.as_view(), name="dashboard_pedidos"),
]

#urlpatterns = router.urls
