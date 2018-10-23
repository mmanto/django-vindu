from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import *
from .forms  import *
from carrito.models import Pedido
from django.utils.safestring import mark_safe

@admin.register(MedioPago)
class MedioPagoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'identificador', 'descripcion', 'imagen']

'''
@admin.register(ImporteFijoEnvioCABA)
class ImporteFijoEnvioCABAAdmin(SingletonModelAdmin):
    model = ImporteFijoEnvioCABA
    list_display = ['pk', 'importe_fijo_envio_CABA']
'''

@admin.register(TarifaZonaEnvio)
class TarifaZonaEnvioAdmin(admin.ModelAdmin):
    model = TarifaZonaEnvio
    extra = 0
    list_display = ['id_zona', 'nombre_zona', 'tarifa_hasta_1', 'tarifa_hasta_3', 'tarifa_hasta_5',
                    'tarifa_hasta_10']
    ordering = ('id_zona',)

class ProvinciaLocalidadZonaTarifaInline(admin.TabularInline):
    model = ProvinciaLocalidadZonaTarifa
    extra = 0
    exclude = ['zona_tarifa',]
    readonly_fields = ('provincia', 'municipio', 'zona_tarifa_display', 'localidad' )


    def zona_tarifa_display(self, obj):
        return str(obj.zona_tarifa.id_zona) + ' - ' + str(obj.zona_tarifa.nombre_zona)
    zona_tarifa_display.short_description = 'Zona de Tarifa'


@admin.register(CodigoPostal)
class CodigoPostalAdmin(admin.ModelAdmin):
    inlines = [ProvinciaLocalidadZonaTarifaInline,]
    list_display = ['cod_postal', ]
    ordering = ('cod_postal', )
    readonly_fields = ('cod_postal',)
    search_fields = ['cod_postal',]


@admin.register(DescuentoPrimeraCompra)
class DescuentoPrimeraCompraAdmin(SingletonModelAdmin):
    model = DescuentoPrimeraCompra
    list_display = ['importe_fijo_descuento', 'dias_vigencia_descuento']

'''
class VoucherUsadoInline(admin.TabularInline):
    model = VoucherUsado
    form  = VoucherUsadoAdminForm
    extra = 0
    readonly_fields = ('voucher', 'usuario_comprador', 'pedido' )
'''


class VoucherUsadoInline(admin.TabularInline):
    model = Pedido
    extra = 0
    #exclude = ['zona_tarifa',]
    fields = ('nro_pedido', 'usuario_comprador', 'voucher_aplicado',)
    readonly_fields = ('nro_pedido', 'usuario_comprador', 'voucher_aplicado',  )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        list_estados_pagados = ['P', 'E']
        return qs.filter(estado_pedido__in=list_estados_pagados)


@admin.register(Voucher)
class VoucherAdmin(SingletonModelAdmin):
    form = VoucherAdminForm
    inlines = [VoucherUsadoInline,]

    list_display = ('cod_voucher', 'nombre', 'fecha_vigencia_desde', 'fecha_vigencia_hasta', 'importe_minimo_compra', 'importe_voucher',)
    list_display_links = ('cod_voucher',) 
    ordering = ('-fecha_vigencia_hasta', )


@admin.register(TiempoCostoEnvio)
class TiempoCostoEnvioAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', )  
    form = TiempoCostoEnvioAdminForm

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview'  


@admin.register(CuotasFormaPago)
class CuotasFormaPagoAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', )  
    form = CuotasFormaPagoAdminForm

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview' 


@admin.register(CambiosYDevoluciones)
class CambiosYDevolucionesAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', )  
    form = CambiosYDevolucionesAdminForm

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview' 


@admin.register(AcercaVindu)
class AcercaVinduAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', ) 
    form = AcercaVinduAdminForm

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview' 


@admin.register(PoliticasPrivacidad)
class PoliticasPrivacidadAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', )
    form = PoliticasPrivacidadAdminForm  

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview' 


@admin.register(FAQ)
class FAQAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview', )
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', ) 
    form = FAQAdminForm 

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview'


@admin.register(TerminosCondiciones)
class TerminosCondicionesAdmin(SingletonModelAdmin):
    list_display = ('id', 'page_preview',)
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('-id', )
    form = TerminosCondicionesAdminForm 

    def page_preview(self, obj):
        return mark_safe(obj.text_html)
    page_preview.short_description = 'Preview'  




