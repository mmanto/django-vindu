from django.contrib import admin

from .models import PagoMercadoPago
from core.utils import ReadOnlyAdmin


@admin.register(PagoMercadoPago)
class PagoMercadoPagoAdmin(ReadOnlyAdmin):
    search_fields = ('pedido__usuario_comprador__username',)
    readonly_fields = ('pedido',)
    list_display = ('fecha', 'pedido_nro', 'nombre_usuario', 'status', 'transaction_amount')
    list_filter = ('status', 'http_status')
    date_hierarchy = 'fecha'

    def nombre_usuario(self, obj):
        return obj.pedido.usuario_comprador.username
    nombre_usuario.allow_tags = True
    nombre_usuario.short_description = "Usuario comprador"

    def pedido_nro(self, obj):
        return obj.pedido.pk
    pedido_nro.allow_tags = True
    pedido_nro.short_description = "Pedido Nro."

