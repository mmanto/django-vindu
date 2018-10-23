from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.response import Response

from .models import Pedido
from .serializers import PedidoSerializer

class DashboardPedidosView(APIView):
    serializer_class = PedidoSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "carrito/dashboard_pedidos.html"
    permission_classes = (AllowAny,)

    def get(self, request):
        queryset = Pedido.objects.all()
        return Response({'pedidos': queryset})
