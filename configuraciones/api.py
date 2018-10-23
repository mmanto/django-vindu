# -*- encoding: utf-8 -*-
from .models import *
from .serializers import *
from rest_framework import permissions, status, viewsets, exceptions, views, generics
from rest_framework.permissions import (AllowAny, IsAuthenticated)


class GetCodigosPostalesViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = CodigoPostal.objects.all().order_by('pk')
    serializer_class = CodigosPostalesSerializer
    http_method_names = ['get', 'head']

class GetLocalidadesViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProvinciaLocalidadZonaTarifa.objects.all()
    serializer_class = ProvinciaLocalidadZonaTarifaSerializer
    http_method_names = ['get']

    def get_queryset(self):
        queryset = self.queryset
        try:
            cod_postal = self.kwargs['cod_postal']
        except:
            cod_postal = None

        if cod_postal:
            try:
                cod_postal_obj = CodigoPostal.objects.get(cod_postal=cod_postal)
            except:
                queryset = []
            else:
                queryset = queryset.filter(cod_postal_provincia=cod_postal_obj).order_by('pk')

        return queryset


class GetTiempoEnvioViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = TiempoCostoEnvio.objects.all().order_by('pk')
    serializer_class = TiempoCostoEnvioSerializer
    http_method_names = ['get', 'head']

class GetFormasPagoViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = CuotasFormaPago.objects.all().order_by('pk')
    serializer_class = CuotasFormaPagoSerializer
    http_method_names = ['get', 'head']

class GetCambiosDevolucionesViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = CambiosYDevoluciones.objects.all().order_by('pk')
    serializer_class = CambiosDevolucionesSerializer
    http_method_names = ['get', 'head']

class GetAcercaVinduViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = AcercaVindu.objects.all().order_by('pk')
    serializer_class = AcercaVinduSerializer
    http_method_names = ['get', 'head']

class GetPoliticasPrivacidadViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = PoliticasPrivacidad.objects.all().order_by('pk')
    serializer_class = PoliticasPrivacidadSerializer
    http_method_names = ['get', 'head']

class GetFAQViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = FAQ.objects.all().order_by('pk')
    serializer_class = FAQSerializer
    http_method_names = ['get', 'head']

class GetTerminosCondicionesViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = TerminosCondiciones.objects.all().order_by('pk')
    serializer_class = TerminosCondicionesSerializer
    http_method_names = ['get', 'head']

