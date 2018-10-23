# -*- encoding: utf-8 -*-
from django.db import models
from django.utils import timezone


ENTIDAD = (
    ('M', 'Marca'),
    ('V', 'Vindu'),
)

class Obligacion(models.Model):
    pedido = models.ForeignKey('carrito.Pedido', related_name="obligacion_pedido")
    deudor = models.CharField('Deudor', max_length=1, choices=ENTIDAD)
    marca_deudora = models.ForeignKey('mercado_vindu.Marca', on_delete=models.PROTECT, blank=True, null=True, related_name="obligacion_marca_deudora")
    acreedor = models.CharField('Acreedor', max_length=1, choices=ENTIDAD)
    marca_acreedora = models.ForeignKey('mercado_vindu.Marca', on_delete=models.PROTECT, blank=True, null=True, related_name="obligacion_marca_acreedora")
    concepto = models.CharField('Concepto', max_length=50, blank=True, null=True)
    importe_adeudado = models.DecimalField('Importe adeudado', max_digits=15, decimal_places=2)
    estado_liquidacion = models.BooleanField('Estado de liquidación', default=False)
    fecha_liquidacion = models.DateTimeField('Fecha y hora de liquidación', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Obligación"
        verbose_name_plural = "Obligaciones"

    def __str__(self):
        return u'Pedido Nro: %d - Deudor: %s' % (self.pedido.nro_pedido, self.deudor)

    def save(self, *args, **kwargs):
        if self.estado_liquidacion:
            self.fecha_liquidacion = timezone.now()
        else:
            self.fecha_liquidacion = None
        super(Obligacion, self).save()
