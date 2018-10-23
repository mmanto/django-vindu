from django.conf.urls import url
from .api import *
#from rest_framework.routers import DefaultRouter
#from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

#router = DefaultRouter()
urlpatterns = [
    ### API para consulta de códigos postales
    url(r'^get-codigos-postales', GetCodigosPostalesViewSet.as_view({'get': 'list'})),
    ### Esta api debe tomar el cod_postal como request body, response: los ids de provincias/localidades/tarifas por zona
    ### en la siguiente api (SetDomicilioEnvioViewSet) en el request body se debe recibir el id provincia/localidad/zona
    ### luego en set-envio se va a obtener la tarifa de la zona
    ### Luego se actualiza en Pedido los campos zona_tarifa y costo_envio
    url(r'^get-localidades-by-cod_postal/(?P<cod_postal>\d+)', GetLocalidadesViewSet.as_view({'get': 'list'})),
    url(r'^get-tiempo-costo-envio', GetTiempoEnvioViewSet.as_view({'get': 'list'})),
    url(r'^get-cuotas-formas-pago', GetFormasPagoViewSet.as_view({'get': 'list'})),
    url(r'^get-cambios-devoluciones', GetCambiosDevolucionesViewSet.as_view({'get': 'list'})),
    url(r'^get-acerca-vindu', GetAcercaVinduViewSet.as_view({'get': 'list'})),
    url(r'^get-politicas-privacidad', GetPoliticasPrivacidadViewSet.as_view({'get': 'list'})),
    url(r'^get-faq', GetFAQViewSet.as_view({'get': 'list'})),
    url(r'^get-terminos-condiciones', GetTerminosCondicionesViewSet.as_view({'get': 'list'})),


]

#urlpatterns = router.urls-