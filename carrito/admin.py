from django.contrib import admin

from .models import *

class DescuentoInline(admin.TabularInline):
    model = Descuento
    extra = 0
    readonly_fields = ('pedido', 'motivo_descuento', 'importe_descuento')

class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    exclude = ('articulo',)
    readonly_fields = ('pedido', 'producto', 'talle', 'cantidad', 'precio')

    def producto (self, obj):
        return obj.articulo.producto.nombre_producto

    def talle(self, obj):
        return obj.articulo.talle

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [DescuentoInline, LineaPedidoInline]
    list_display = ['nro_pedido', 'marca', 'usuario_comprador', 'importe_pedido',
                    'importe_descuentos', 'importe_total', 'estado_pedido', 'fecha_pedido' ]
    ordering = ('-fecha_pedido', )  
    list_filter = ('marca', 'estado_pedido', 'usuario_comprador')
    list_per_page = 20
    readonly_fields = ('usuario_comprador', 'zona_tarifa', 'iflow_tracking_id',
                       'url_pago_MP', 'iflow_cod_etiqueta', 'iflow_print_url', 'date_created', 'date_updated',
                       'env_nombre', 'env_apellido', 'env_calle', 'env_numero', 'env_piso', 'env_departamento',
                       'env_provincia', 'env_localidad_ref', 'env_cod_postal',
                       'fac_nombre', 'fac_apellido', 'fac_calle', 'fac_numero', 'fac_piso', 'fac_departamento',
                       'fac_provincia', 'fac_localidad_ref', 'fac_cod_postal', )                      
 
