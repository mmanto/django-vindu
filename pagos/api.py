# -*- encoding: utf-8 -*-
from rest_framework import permissions, status, viewsets, exceptions, views, generics
#from .serializers import *
from rest_framework.response import Response
from .models import *
import requests
import mercadopago


class MP_PagoExitosoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'head']

    def list(self, second_param):
        nro_pedido = self.request.GET.get('r', None)
        return Response({"success": "Pago exitoso."},
                        status=status.HTTP_200_OK)

class MP_PagoErroneoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'head']

    def list(self, second_param):
        nro_pedido = self.request.GET.get('r', None)
        return Response({"error": "Pago erróneo"}, status=status.HTTP_400_BAD_REQUEST)

class MP_PagoPendienteViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'head']

    def list(self, second_param):
        nro_pedido = self.request.GET.get('r', None)
        return Response({"error": "Pago pendiente"}, status=status.HTTP_400_BAD_REQUEST)

class MP_PagoRechazadoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    permission_classes = (permissions.AllowAny,)
    http_method_names = ['get', 'head']

    def list(self, second_param):
        nro_pedido = self.request.GET.get('r', None)
        return Response({"error": "Pago rechazado"}, status=status.HTTP_400_BAD_REQUEST)