from django.db import models
from datetime import date
from mercado_vindu.models import Deposito
from django.conf import settings
from rest_framework.response import Response
from rest_framework import permissions, status
import requests
import json
import simplejson
from decimal import *


ESTADOS_PEDIDO = (
    (u'I', u'Pendiente de pago'),   # I:Impago
    (u'P', u'Pendiente de entrega'),
    (u'E', u'Entregado'), 
    (u'C', u'Cancelado'), 
    (u'D', u'Devuelto'), 
    )
CARGO_COSTO = (
    (u'A', u'Costo de envío a cargo de Anting'),
    (u'M', u'Costo de envío a cargo de la Marca'), 
    )

RESPONSABLE_ENVIO = (
    (u'A', u'Anting'),
    (u'I', u'IFlow'), 
    )      

class Carrito(models.Model):
    usuario_comprador = models.OneToOneField('auth_api.UserComprador', on_delete=models.PROTECT, related_name="carrito_user_comprador", primary_key=True)
    importe_descuentos = models.DecimalField('Importe de descuentos', max_digits=15, decimal_places=2, default=0)
    importe_dto_primera_compra = models.DecimalField('Importe de descuento por primera compra', max_digits=15, decimal_places=2, default=0)
    voucher_aplicado = models.ForeignKey('configuraciones.Voucher', on_delete=models.PROTECT, related_name="carrito_voucher_aplicado", blank=True, null=True)

    flag_regalo = models.BooleanField('Es un regalo?', default=False)

    # Relación con Depósito de la Marca
    deposito_marca = models.ForeignKey('mercado_vindu.Deposito', on_delete=models.PROTECT, related_name="carrito_deposito_marca", blank=True, null=True)

    # Datos y domicilio de envío del pedido
    # Datos adicionales para el envío
    # Usuario que recibe el pedido en caso que sea un regalo
    usuario_receptor_regalo = models.ForeignKey('auth_api.UserComprador', on_delete=models.PROTECT, related_name="carrito_user_regalado", blank=True, null=True)
    domicilio_envio = models.ForeignKey('Domicilio', on_delete=models.PROTECT, blank=True, null=True, related_name="carrito_dom_envio")
    entre_1 = models.CharField('Calle lateral 1 o intersección de destinatario', max_length=25, blank=True, null=True)
    entre_2 = models.CharField('Calle lateral 2', max_length=25, blank=True, null=True)
    telefono_contacto = models.CharField('Teléfono de contacto', max_length=50, blank=True, null=True)
    fecha_solicitada_entrega = models.DateField('Fecha solicitada de entrega', blank=True, null=True)
    comentarios_pedido = models.TextField('Comentarios sobre el pedido', blank=True, null=True, max_length=150)
    zona_tarifa = models.ForeignKey('configuraciones.ProvinciaLocalidadZonaTarifa', on_delete=models.PROTECT, related_name="carrito_tarifa_zona", blank=True, null=True)
    cargo_costo_envio = models.CharField('Cargo costo del envio', max_length=1, choices=CARGO_COSTO, default='A')
    costo_envio = models.DecimalField('Costo del envío', max_digits=8, decimal_places=2, blank=True, default=0, null=True)
    responsable_envio = models.CharField('Responsable del envio', max_length=1, choices=RESPONSABLE_ENVIO, default='A')

    # Domicilio de facturacion
    domicilio_facturacion = models.ForeignKey('Domicilio', on_delete=models.PROTECT, blank=True, null=True, related_name="carrito_dom_facturacion")


    class Meta:
        verbose_name = "Carrito de Compras"
        verbose_name_plural = "Carritos de Compras"

    def __unicode__(self):
        return u'%s' % (self.usuario_comprador.username)

    @property
    def _items_dict(self):
        items_dict = {}

        qs_lineas_carrito = ItemCarrito.objects.filter(carrito=self)
        for linea_carrito_obj in qs_lineas_carrito:
            items_dict[linea_carrito_obj.articulo.pk] = linea_carrito_obj

        return items_dict

    @property
    def items(self):
        """
        The list of cart items.
        """
        return self._items_dict.values()

    def clear(self):
        """
        Removes all items.
        """
        qs_lineas_carrito = ItemCarrito.objects.filter(carrito=self)
        qs_lineas_carrito.delete()

    @property
    def unique_count(self):
        """
        The number of unique items in cart, regardless of the quantity.
        """
        return len(self._items_dict)

    @property
    def is_empty(self):
        return self.unique_count == 0

    @property
    def products(self):
        """
        The list of associated products.
        """
        return [item.articulo for item in self.items]

    def get_marca(self):
        primer_articulo = self.products[0]
        return primer_articulo.producto.marca

    def add(self, articulo, cantidad=1):
        cantidad = int(cantidad)
        if cantidad < 1:
            raise ValueError('La cantidad debe ser al menos 1')


        if articulo in self.products:
            self._items_dict[articulo.pk].cantidad += cantidad
            linea_carrito_obj = ItemCarrito.objects.get(carrito=self, articulo=articulo)
            linea_carrito_obj.cantidad += cantidad
        else:
            linea_carrito_obj, created = ItemCarrito.objects.get_or_create(
                                        carrito = self,
                                        articulo = articulo,
                                        cantidad = cantidad)

            self._items_dict[articulo.pk] = linea_carrito_obj

        linea_carrito_obj.save()

    def set_quantity(self, articulo, cantidad):
        """
        Sets the product's quantity.
        """
        cantidad = int(cantidad)
        if cantidad < 0:
            raise ValueError('La cantidad debe ser un número mayor que 0')
        if articulo in self.products:
            linea_carrito_obj = ItemCarrito.objects.get(carrito=self, articulo=articulo)
            self._items_dict[articulo.pk].cantidad = cantidad
            if self._items_dict[articulo.pk].cantidad < 1:
                del self._items_dict[articulo.pk]
                linea_carrito_obj.delete()
            else:
                linea_carrito_obj.cantidad = cantidad
                linea_carrito_obj.save()

    def remove(self, articulo):
        """
        Removes the product.
        """
        if articulo in self.products:
            del self._items_dict[articulo.pk]
            linea_carrito_obj = ItemCarrito.objects.get(carrito=self, articulo=articulo)
            linea_carrito_obj.delete()

    @property
    def count(self):
        """
        The number of items in cart, that's the sum of quantities.
        """
        return sum([item.cantidad for item in self.items])

    @property
    def total(self):
        """
        The total value of all items in the cart.
        """
        return sum([item.subtotal for item in self.items])


class ItemCarrito(models.Model):
    carrito = models.ForeignKey('Carrito', on_delete=models.CASCADE, related_name="carrito_linea_carrito")
    articulo  = models.ForeignKey('mercado_vindu.TalleProducto')
    cantidad  = models.IntegerField('Cantidad')
    # El precio debe ser el vigente del producto
    #precio    = models.DecimalField('Precio', max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Item del Carrito"
        verbose_name_plural = "Items del Carrito"

    def __str__(self):
        return u'%s' - u'%s' % (self.carrito, self.articulo.producto.nombre_producto)

    @property
    def precio(self):
        return self.articulo.producto.get_precio_actual()

    @property
    def subtotal(self):
        """
        Subtotal for the cart item.
        """
        return self.precio * self.cantidad


class Pedido(models.Model):
    nro_pedido = models.AutoField('Número de Pedido', primary_key=True)
    marca = models.ForeignKey('mercado_vindu.Marca')
    proveedor_pago = models.CharField('Proveedor de pagos', max_length=2, choices=settings.PROVEEDORES_PAGO, default='MP')
    usuario_comprador = models.ForeignKey('auth_api.UserComprador', on_delete=models.PROTECT, related_name="pedido_user_comprador")
    #importe_pedido = models.DecimalField('Importe del Pedido', max_digits=15, decimal_places=2)
    importe_descuentos = models.DecimalField('Importe de descuentos', max_digits=15, decimal_places=2, default=0)
    #importe_total = models.DecimalField('Importe Total del Pedido con descuentos', max_digits=15, decimal_places=2)
    estado_pedido = models.CharField('Estado del Pedido', max_length=1, choices=ESTADOS_PEDIDO, default='I')
    fecha_pedido = models.DateField('Fecha de confección del Pedido', default=date.today)
    fecha_pago   = models.DateField('Fecha de pago del Pedido', blank=True, null=True)
    comprobante_mercadopago = models.CharField(max_length=255, blank=True, null=True)
    fecha_pedido_entregado = models.DateField('Fecha en que el pedido fue entregado', blank=True, null=True) 
    comision_vindu = models.DecimalField('Importe de comisión Vindu', max_digits=6, decimal_places=2, default=0)
    voucher_aplicado = models.ForeignKey('configuraciones.Voucher', on_delete=models.PROTECT, related_name="pedido_voucher_aplicado", blank=True, null=True)

    flag_regalo = models.BooleanField('Es un regalo?', default=False)

    # Relación con Depósito de la Marca
    deposito_marca = models.ForeignKey('mercado_vindu.Deposito', on_delete=models.PROTECT, related_name="pedido_deposito_marca", blank=True, null=True)

    # Datos y domicilio de envío del pedido
    # Datos adicionales para el envío
    # Usuario que recibe el pedido en caso que sea un regalo
    usuario_receptor_regalo = models.ForeignKey('auth_api.UserComprador', on_delete=models.PROTECT, related_name="pedido_user_regalado", blank=True, null=True)
    #domicilio_envio = models.ForeignKey('Domicilio', on_delete=models.PROTECT, blank=True, null=True, related_name="pedido_dom_envio")
    env_nombre = models.CharField('Nombre', max_length=50, blank=True, null=True)
    env_apellido = models.CharField('Apellido', max_length=50, blank=True, null=True)
    env_calle = models.CharField('Calle', max_length=50, blank=True, null=True)
    env_numero = models.CharField('Número', max_length=10, blank=True, null=True)
    env_piso = models.CharField('Piso', max_length=6, blank=True, null=True)
    env_departamento = models.CharField('Departamento', max_length=4, blank=True, null=True)
    env_provincia = models.CharField('Provincia', max_length=25, blank=True, null=True)
    env_localidad_ref = models.ForeignKey('configuraciones.ProvinciaLocalidadZonaTarifa', related_name="env_localidad_ref", blank=True, null=True)
    env_cod_postal = models.ForeignKey('configuraciones.CodigoPostal', on_delete=models.PROTECT, related_name="env_domicilio_tarifa_zona", blank=True, null=True)


    entre_1 = models.CharField('Calle lateral 1 o intersección de destinatario', max_length=25, blank=True, null=True)
    entre_2 = models.CharField('Calle lateral 2', max_length=25, blank=True, null=True)
    telefono_contacto = models.CharField('Teléfono de contacto', max_length=50, blank=True, null=True)
    fecha_solicitada_entrega = models.DateField('Fecha solicitada de entrega', blank=True, null=True)
    comentarios_pedido = models.TextField('Comentarios sobre el pedido', blank=True, null=True, max_length=150)
    zona_tarifa = models.ForeignKey('configuraciones.ProvinciaLocalidadZonaTarifa', on_delete=models.PROTECT, related_name="pedido_tarifa_zona", blank=True, null=True)
    cargo_costo_envio = models.CharField('Cargo costo del envio', max_length=1, choices=CARGO_COSTO, default='A')
    costo_envio = models.DecimalField('Costo del envío', max_digits=8, decimal_places=2, blank=True, default=0, null=True)
    responsable_envio = models.CharField('Responsable del envio', max_length=1, choices=RESPONSABLE_ENVIO, default='A')

    # Domicilio de facturacion
    #domicilio_facturacion = models.ForeignKey('Domicilio', on_delete=models.PROTECT, blank=True, null=True, related_name="pedido_dom_facturacion")
    fac_nombre = models.CharField('Nombre', max_length=50, blank=True, null=True)
    fac_apellido = models.CharField('Apellido', max_length=50, blank=True, null=True)
    fac_calle = models.CharField('Calle', max_length=50, blank=True, null=True)
    fac_numero = models.CharField('Número', max_length=10, blank=True, null=True)
    fac_piso = models.CharField('Piso', max_length=6, blank=True, null=True)
    fac_departamento = models.CharField('Departamento', max_length=4, blank=True, null=True)
    fac_provincia = models.CharField('Provincia', max_length=25, blank=True, null=True)
    fac_localidad_ref = models.ForeignKey('configuraciones.ProvinciaLocalidadZonaTarifa', related_name="fac_localidad_ref", blank=True, null=True)
    fac_cod_postal = models.ForeignKey('configuraciones.CodigoPostal', on_delete=models.PROTECT, related_name="fac_domicilio_tarifa_zona", blank=True, null=True)


    # Datos del pago
    #estado_pago = models.CharField('Estado del pago', max_length=3, choices=ESTADOS_PAGO, default='PEN')
    #medio_pago = models.ForeignKey('configuraciones.MedioPago', blank=True, null=True)
    #fecha_pago = models.DateTimeField('Fecha de pago', blank=True, null=True) 

    # Datos de MercadoPago
    url_pago_MP = models.URLField('Init point MP', blank=True, null=True) 
    # Datos de PayU
    url_pago_PU = models.URLField('Init point PU', blank=True, null=True) 

    # Datos de la orden generada en IFlow
    iflow_tracking_id = models.CharField('Tracking Id en Iflow', max_length=50, blank=True, null=True)
    iflow_cod_etiqueta = models.CharField('Código de la etiqueta', max_length=50, blank=True, null=True)
    iflow_print_url = models.CharField('URL de la etiqueta', max_length=150, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __unicode__(self):
        return u'%s' % (self.nro_pedido)

    def __str__(self):
        return u'%s' % (self.nro_pedido)

    @property
    def cantidad_productos_pedidos(self):
        """
        Devuelve la cantidad de productos pedidos
        """
        qs_lineas = LineaPedido.objects.filter(pedido=self)
        return sum([x.cantidad for x in qs_lineas])

    @property
    def importe_pedido(self):
        """
        Devuelve la suma de los importes de los articulos pedidos
        Si el pedido está impago se toman los precios vigentes, si no los históricos
        """
        qs_lineas = LineaPedido.objects.filter(pedido=self)
        suma_importes = 0
        if self.estado_pedido == 'I':
            for linea in qs_lineas:
                suma_importes += linea.cantidad * linea.articulo.producto.get_precio_actual()
        else:
            for linea in qs_lineas:
                suma_importes += linea.cantidad * linea.precio

        return round(suma_importes, 2)

    @property
    def importe_total(self):
        importe_total = self.importe_pedido - self.importe_descuentos 
        if self.responsable_envio == 'A' and self.costo_envio: 
            importe_total += self.costo_envio

        return round(importe_total, 2)

    @property
    def cargo_costo_envio_comprador(self):
        if self.responsable_envio == 'A' and self.costo_envio: 
            return self.costo_envio
        else:
            return Decimal(0)

    @property
    def productos(self):
        """
        Devuelve los productos del pedido
        """
        productos = self.articulos_pedido.all().values_list('articulo__producto__nombre_producto', flat=True)
        return ' - '.join(productos)

    def save(self, **kwargs):
        marca = self.marca
        deposito_default = Deposito.objects.get(marca=marca, ind_deposito_default=True)
        self.deposito_marca = deposito_default 
        super(Pedido, self).save(**kwargs)

    def autenticar_en_iflow(self, request):
        # Autenticación y obtención del token en IFlow
        url = settings.HOST_IFLOW + 'login'
        params = {'_username': settings.USERNAME_IFLOW, '_password': settings.PSW_IFLOW}
        print('url: ', url)
        print('params: ', params)
        r = requests.post(url, json=params)
        print('r: ', r)
        print('r.text: ', r.text)
        print('r.status_code: ', r.status_code)

        if r.status_code != 200:
            response = Response({"error": "Autenticación en IFlow fallida"}, status=r.status_code)
            return response.__dict__

        # status_code == 200 - response Ok
        data = r.json()
        print('dict de response: ', r.__dict__)
        print('resultado data: ', data)
        access_token = data['token']
        print('access_token: ', access_token)  
        return access_token      

    def crear_orden_iflow(self, access_token, request):
        # Con el access_token de IFlow se llama API para crear el envío
        url = settings.HOST_IFLOW + 'order/create'
        header={'Authorization': 'Bearer %s' %  access_token}

        items = []
        pedido_obj = self
        qs_lineas_pedido = LineaPedido.objects.filter(pedido=pedido_obj)
        for linea_pedido in qs_lineas_pedido:
            dict_articulo = {'item': linea_pedido.articulo.producto.nombre_producto,
                             'sku' : linea_pedido.articulo.shop_sku,
                             'quantity': linea_pedido.cantidad}
            items.append(dict_articulo)

        dict_shipments = {
            'items_value': simplejson.dumps(pedido_obj.importe_total),
            'shipping_cost': simplejson.dumps(pedido_obj.costo_envio),
            # TODO: verificar estos parámetros
            'width': 20,
            'height': 20,
            'length': 20,
            'weight': 3000,
            # HASTA ACA
            'items': items
        }

        zona_tarifa = self.zona_tarifa
        if not zona_tarifa:
            response = Response({"error": "Zona de tarifa no informada en el Pedido"}, status=status.HTTP_400_BAD_REQUEST)
            return response.__dict__

        domicilio_envio = self.domicilio_envio
        if not domicilio_envio:
            response = Response({"error": "Domicilio de envío no informado en el Pedido"}, status=status.HTTP_400_BAD_REQUEST)
            return response.__dict__

        receiver_address = {
            'street_name': domicilio_envio.calle,
            'street_number': domicilio_envio.numero,
            'between_1': self.entre_1,
            'other_info': self.comentarios_pedido,
            'neighborhood_name': zona_tarifa.localidad,
            'zip_code': domicilio_envio.cod_postal.cod_postal,
            'city': zona_tarifa.municipio
        }
        if self.entre_2:
            receiver_address['between_2'] = self.entre_2

        receiver = {
            'first_name': domicilio_envio.nombre,
            'last_name' : domicilio_envio.apellido,
            'receiver_name': domicilio_envio.nombre + ' ' + domicilio_envio.apellido,
            'receiver_phone': self.telefono_contacto,
            'email': self.usuario_comprador.email,
            'address': receiver_address
        }

        params = {
            'order_id': self.nro_pedido,
            'shipments': [dict_shipments],
            'receiver' : receiver,
        }

        print('url: ', url)
        print('params: ', json.dumps(params))
        print('header: ', header)
        r = requests.post(url, headers=header, data=json.dumps(params))

        if r.status_code != 201:
            response = Response({"error": "La orden no pudo ser creada"}, status=r.status_code)
            return response.__dict__

        # status_code == 201 - response Ok - orden creada
        data = r.json()
        print('resultado data: ', data)

        results = data['results']
        print('results: ', results)  

        pedido_obj.iflow_tracking_id = results['tracking_id']
        list_paquetes = results['shippings']
        primer_paquete = list_paquetes[0]
        pedido_obj.iflow_cod_etiqueta = primer_paquete['shipment_id']
        pedido_obj.iflow_print_url = primer_paquete['print_url']
        pedido_obj.save()

        return r


class Descuento(models.Model):
    pedido    = models.ForeignKey('Pedido', on_delete=models.CASCADE, related_name="descuento_pedido")
    motivo_descuento = models.CharField('Motivo del descuento', max_length=50)
    importe_descuento = models.DecimalField('Importe del descuento', max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Descuento"
        verbose_name_plural = "Descuentos"

    def __unicode__(self):
        return u'%s - %s' % (self.pedido, self.motivo_descuento)


class LineaPedido(models.Model):
    pedido    = models.ForeignKey('Pedido', on_delete=models.PROTECT, related_name="articulos_pedido")
    articulo  = models.ForeignKey('mercado_vindu.TalleProducto', on_delete=models.PROTECT)
    cantidad  = models.IntegerField('Cantidad')
    precio    = models.DecimalField('Precio', max_digits=15, decimal_places=2)

    class Meta:
        verbose_name = "Línea de Pedido"
        verbose_name_plural = "Líneas de Pedido"

    def __str__(self):
        return u'%s - %s' % (self.pedido, self.articulo)


class Domicilio(models.Model):     
    usuario_comprador = models.ForeignKey('auth_api.UserComprador', on_delete=models.PROTECT, related_name="domicilio_user_comprador")
    nombre = models.CharField('Nombre', max_length=50, blank=True, null=True)
    apellido = models.CharField('Apellido', max_length=50, blank=True, null=True)
    calle = models.CharField('Calle', max_length=50, blank=True, null=True)
    numero = models.CharField('Número', max_length=10, blank=True, null=True)
    piso = models.CharField('Piso', max_length=6, blank=True, null=True)
    departamento = models.CharField('Departamento', max_length=4, blank=True, null=True)
    provincia = models.CharField('Provincia', max_length=25, blank=True, null=True)
    #localidad = models.CharField('Localidad', max_length=50, blank=True, null=True)
    localidad_ref = models.ForeignKey('configuraciones.ProvinciaLocalidadZonaTarifa', blank=True, null=True)
    cod_postal = models.ForeignKey('configuraciones.CodigoPostal', on_delete=models.PROTECT, related_name="domicilio_tarifa_zona", blank=True, null=True)

    class Meta:
        verbose_name = "Domicilio"
        verbose_name_plural = "Domicilios"

    def __str__(self):
        return '%s %s - %s %s, %s' % (self.nombre, self.apellido, self.calle, self.numero, self.localidad_ref.localidad)

