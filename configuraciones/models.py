from django.db import models
from django.utils.encoding import smart_text
from solo.models import SingletonModel
from datetime import timedelta, datetime, date
from django.utils import timezone
from carrito.models import Carrito, Pedido

def validate_non_negative(value):
    if value < 0:
        raise ValidationError(
            _('Este campo no puede ser negativo')
        )

class MedioPago(models.Model):

    nombre = models.CharField('Nombre', max_length=20)
    identificador = models.CharField('Identificador', max_length=20)
    comision = models.DecimalField('Porcentaje de comision',
                                   help_text="Ej: 5 (para 5%)", max_digits=10,
                                   decimal_places=2, default=0)
    precio_en_dolares = models.BooleanField('Precio en dolares', help_text='Se debe convertir el precio a dolares',
                                            default=False)
    descripcion = models.TextField('Descripción', blank=True)
    imagen = models.ImageField(upload_to='imagenes_medios_de_pago', blank=True, default=None)

    def __unicode__(self):
        return smart_text(self.nombre)

    class Meta:
        verbose_name = 'Medio de Pago'
        verbose_name_plural = 'Medios de Pago'

class TarifaZonaEnvio(models.Model):
    id_zona = models.IntegerField('Id de la zona', primary_key=True)
    nombre_zona = models.CharField('Nombre de la zona', max_length=20)
    tarifa_hasta_1 = models.DecimalField('Tarifa hasta 1 Kg', validators=[validate_non_negative],
                            max_digits=15, decimal_places=2, help_text='Tarifa hasta 1 Kg')
    tarifa_hasta_3 = models.DecimalField('Tarifa hasta 3 Kg', validators=[validate_non_negative],
                            max_digits=15, decimal_places=2, help_text='Tarifa hasta 3 Kg') 
    tarifa_hasta_5 = models.DecimalField('Tarifa hasta 5 Kg', validators=[validate_non_negative],
                            max_digits=15, decimal_places=2, help_text='Tarifa hasta 5 Kg')  
    tarifa_hasta_10 = models.DecimalField('Tarifa hasta 10 Kg', validators=[validate_non_negative],
                            max_digits=15, decimal_places=2, help_text='Tarifa hasta 10 Kg')    
    plazo_entrega   = models.CharField('Plazo de entrega', max_length=50, blank=True, null=True)     

    class Meta:
        verbose_name = 'Tarifas para Zona de Envío'
        verbose_name_plural = 'Tarifas para Zonas de Envíos'

    '''
    def __unicode__(self):
        return '%s' - '%s'  % (smart_text(self.id_zona), smart_text(self.nombre_zona))
    '''

    def __str__(self):
        return format(self.id_zona)+' - '+format(self.nombre_zona)
        

class CodigoPostal(models.Model):
    cod_postal = models.IntegerField('Código Postal', primary_key=True)
    #codigo_region = models.CharField('Código de región', max_length=4)
    #municipio = models.CharField('Municipio', max_length=50)
    #zona_tarifa = models.ForeignKey('TarifaZonaEnvio')
    #localidad = models.CharField('Localidad', max_length=50)

    def __str__(self):
        return smart_text(self.cod_postal)

    class Meta:
        verbose_name = 'Código Postal'
        verbose_name_plural = 'Códigos Postales'


class ProvinciaLocalidadZonaTarifa(models.Model):
    cod_postal_provincia = models.ForeignKey('CodigoPostal')
    provincia = models.CharField('Provincia', max_length=25)
    municipio = models.CharField('Municipio', max_length=50)
    zona_tarifa = models.ForeignKey('TarifaZonaEnvio')
    localidad = models.CharField('Localidad', max_length=50)

    '''
    def __unicode__(self):
        return '%s' - '%s' - '%s' - '%s' % (smart_text(self.provincia), smart_text(self.municipio), smart_text(self.zona_tarifa), smart_text(self.localidad))
    '''

    def __str__(self):
    #    return format(self.provincia)+' - '+format(self.municipio)+' - '+format(self.zona_tarifa)+' - '+format(self.localidad)
        return ''

    class Meta:
        verbose_name = 'Provincia, Municipio, Localidad y Tarifa de Zona'
        verbose_name_plural = 'Provincias, Municipios, Localidades y Tarifas de Zona'

class DescuentoPrimeraCompra(SingletonModel):

    importe_fijo_descuento = models.DecimalField('Importe fijo de descuento por primera compra',
                                                   max_digits=15, decimal_places=2, default=0)
    dias_vigencia_descuento = models.IntegerField('Días de vigencia del descuento', validators=[validate_non_negative],
                             default=0, help_text='Cantidad de días contando desde la registración del usuario')

    class Meta:
        verbose_name = 'Descuento por primera compra'

    def __str__(self):
        return smart_text(self.importe_fijo_descuento)

    def descuento_primera_compra(self, usuario_comprador):
        fecha_registracion = usuario_comprador.date_joined
        timedelta_hasta = timedelta(days=self.dias_vigencia_descuento)
        fecha_tope_descuento = fecha_registracion + timedelta_hasta
        #fecha_hoy = datetime.now()
        fecha_hoy = timezone.now()

        if fecha_hoy <= fecha_tope_descuento:
            descuento = self.importe_fijo_descuento
        else:
            descuento = 0

        return descuento


class Voucher(models.Model):
    cod_voucher = models.CharField('Código de Voucher', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=100)
    fecha_vigencia_desde = models.DateField('Fecha de vigencia desde')
    fecha_vigencia_hasta = models.DateField('Fecha de vigencia hasta') 
    importe_minimo_compra = models.DecimalField('Importe mínimo de compra', max_digits=15, decimal_places=2, default=0)
    importe_voucher = models.DecimalField('Importe de descuento del voucher', max_digits=15, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'

    def __str__(self):
        return smart_text(self.cod_voucher)

    def check_voucher_aplicable(self, carrito_obj):
        if carrito_obj.importe_descuentos > 0:
            return False, "Los vouchers no son acumulables con otros descuentos"

        fecha_hoy = date.today()
        if self.fecha_vigencia_desde > fecha_hoy or fecha_hoy > self.fecha_vigencia_hasta:
            return False, "Voucher no vigente"

        usuario_comprador = carrito_obj.usuario_comprador
        list_estados_pagados = ['P', 'E']
        qs_count_this_voucher = Pedido.objects.filter(usuario_comprador=usuario_comprador, voucher_aplicado=self,
                                estado_pedido__in=list_estados_pagados).count()
        if qs_count_this_voucher > 0:
            return False, "Voucher ya utilizado"

        if self.importe_minimo_compra > carrito_obj.total:
            return False, "El pedido no supera el monto mínimo de compra requerido"

        return True, "Voucher aplicable"


'''
class VoucherUsado(models.Model):
    voucher = models.ForeignKey(Voucher, on_delete=models.PROTECT, related_name="voucher_voucher_usado")
    usuario_comprador = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_voucher_usado")
    pedido = models.ForeignKey('carrito.Pedido', on_delete=models.PROTECT, related_name="pedido_voucher_usado")

    def __str__(self):
        return '%s' - '%s' - '%s' % (smart_text(self.voucher.cod_voucher), smart_text(self.usuario_comprador.username), smart_text(self.pedido.nro_pedido))

    class Meta:
        verbose_name = 'Voucher Utilizado'
        verbose_name_plural = 'Vouchers Utilizados'
'''


class TiempoCostoEnvio(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Tiempo y Costo de Envío"
        verbose_name_plural = "Tiempos y Costos de Envío"

class CuotasFormaPago(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Cuotas y Formas de Pago"
        verbose_name_plural = "Cuotas y Formas de Pago"

class CambiosYDevoluciones(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Cambios y Devoluciones"
        verbose_name_plural = "Cambios y Devoluciones"

class AcercaVindu(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Acerca de Vindu"
        verbose_name_plural = "Acerca de Vindu"

class PoliticasPrivacidad(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Políticas de Privacidad"
        verbose_name_plural = "Políticas de Privacidad"

class FAQ(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"

class TerminosCondiciones(SingletonModel):
    text_html = models.TextField('Texto HTML')

    class Meta:
        verbose_name = "Términos y Condiciones"
        verbose_name_plural = "Términos y Condiciones"
