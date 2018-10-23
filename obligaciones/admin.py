from django.contrib import admin

from .models import *

@admin.register(Obligacion)
class ObligacionAdmin(admin.ModelAdmin):
    list_display = ['pedido', 'deudor', 'acreedor', 'concepto', 'importe_adeudado',
                    'estado_liquidacion', 'fecha_liquidacion', 'date_updated', ]
    ordering = ('-date_updated', )  
    list_filter = ('estado_liquidacion', 'pedido__marca', 'pedido',  )
    list_per_page = 20
    readonly_fields = ('fecha_liquidacion', )

