# -*- encoding: utf-8 -*-
from rest_framework import serializers, exceptions
from .models import *
#from configuraciones.models import Provincia
from configuraciones.models import CodigoPostal, ProvinciaLocalidadZonaTarifa
from auth_api.serializers import UserCompradorUsernameSerializer
#from configuraciones.serializers import ProvinciaSerializer
from rest_framework.settings import api_settings
from configuraciones.serializers import ProvinciaLocalidadZonaTarifaSerializer
from mercado_vindu.serializers import DepositoSerializer


class DomicilioDisplaySerializer(serializers.ModelSerializer):
    usuario_comprador = UserCompradorUsernameSerializer(read_only=True, many=False)
    cod_postal = serializers.SerializerMethodField()
    localidad = serializers.SerializerMethodField()

    def get_cod_postal(self, obj):
        return obj.cod_postal.cod_postal

    def get_localidad(self, obj):
        if obj.localidad_ref:
            return obj.localidad_ref.localidad
        else: 
            return None

    class Meta:
        model = Domicilio
        fields = ('id', 'usuario_comprador', 'nombre', 'apellido', 'calle', 'numero', 'piso', 'departamento',
                'provincia', 'localidad', 'cod_postal') 

class CarritoSerializer(serializers.Serializer):
    usuario = serializers.SerializerMethodField()
    cantidad_articulos = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    importe_total = serializers.SerializerMethodField()
    voucher_aplicado = serializers.SerializerMethodField()
    domicilio_envio = DomicilioDisplaySerializer(read_only=True, many=False)
    cargo_costo_envio = serializers.SerializerMethodField()
    costo_envio = serializers.SerializerMethodField()
    responsable_envio = serializers.SerializerMethodField()
    entre_1 = serializers.SerializerMethodField() 
    entre_2 = serializers.SerializerMethodField() 
    telefono_contacto = serializers.SerializerMethodField()
    comentarios_pedido = serializers.SerializerMethodField()   
    domicilio_facturacion = DomicilioDisplaySerializer(read_only=True, many=False)
    descuentos  = serializers.SerializerMethodField()
    domicilio_remitente = serializers.SerializerMethodField()
    lineas_carrito  = serializers.SerializerMethodField()

    def _get_foto_or_null(self, foto_obj):
        try:
            url = foto_obj.url
        except:
            return ''
        else:
            request = self.context.get('request')
            photo_url = foto_obj.url
            return request.build_absolute_uri(photo_url)

    def get_usuario(self, obj):
        request = self.context.get('request')
        user_auth = request.user 

        return user_auth.username

    def get_cantidad_articulos(self, obj):
        return obj.count

    def get_marca(self, obj):
        try:
            marca = obj.get_marca()
        except:
            return None
        else:
            return marca.nombre


    def get_importe_total(self, obj):
        importe_total = obj.total - obj.importe_descuentos
        if obj.cargo_costo_envio == 'A' and obj.costo_envio > 0:
            importe_total += obj.costo_envio
        return importe_total

    def get_voucher_aplicado(self, obj):
        if obj.voucher_aplicado:
            return obj.voucher_aplicado.cod_voucher
        else:
            return None

    def get_cargo_costo_envio(self, obj):
        return obj.get_cargo_costo_envio_display()

    def get_costo_envio(self, obj):
        return obj.costo_envio

    def get_responsable_envio(self, obj):
        return obj.get_responsable_envio_display() 

    def get_entre_1(self, obj):
        return obj.entre_1

    def get_entre_2(self, obj):
        return obj.entre_2

    def get_telefono_contacto(self, obj):
        return obj.telefono_contacto

    def get_comentarios_pedido(self, obj):
        return obj.comentarios_pedido

    def get_descuentos(self, obj):
        return obj.importe_descuentos

    def get_cant_productos(self, obj):
        return obj.count

    def get_domicilio_remitente(self, obj):
        try:
            primer_linea_carrito = obj.products[0]
        except:
            return None
        else:
            marca = primer_linea_carrito.producto.marca

        deposito_default = marca.get_deposito_default()
        if deposito_default:
            return DepositoSerializer(instance=deposito_default).data
        else:
            return None

    def get_lineas_carrito(self, obj):
        lineas_carrito = []
        for item in obj.items:
            item_dict = {'articulo_id': item.articulo.id,
                         'nombre_producto': item.articulo.producto.nombre_producto,
                         'talle': item.articulo.talle,
                         'color': item.articulo.producto.color,
                         'producto_id': item.articulo.producto.id,
                         'codigo_producto': item.articulo.producto.cod_producto,
                         'shop_sku': item.articulo.shop_sku,
                         'foto_principal': self._get_foto_or_null(item.articulo.producto.foto_principal),
                         'cantidad': item.cantidad,
                         'precio': item.precio}
            lineas_carrito.append(item_dict)

        return lineas_carrito 

class AgregarArticuloSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(required=True, min_value=0)
    articulo_id = serializers.IntegerField(required=True)

class CarritoDetalleSerializer(serializers.Serializer):
    cantidad = serializers.IntegerField(required=True, min_value=1)


class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = ('motivo_descuento', 'importe_descuento',)


class PedidoSerializer(serializers.ModelSerializer):
    nro_pedido = serializers.SerializerMethodField()
    usuario = serializers.SerializerMethodField()
    marca   = serializers.SerializerMethodField()
    cantidad_articulos = serializers.SerializerMethodField()
    estado_pedido = serializers.SerializerMethodField()
    voucher_aplicado = serializers.SerializerMethodField()
    lineas_pedido  = serializers.SerializerMethodField()
    domicilio_envio = serializers.SerializerMethodField()
    cargo_costo_envio = serializers.SerializerMethodField()
    domicilio_facturacion = serializers.SerializerMethodField()
    email_destinatario = serializers.SerializerMethodField()
    descuentos  = DescuentoSerializer(read_only=True, many=True, source='descuento_pedido')
    responsable_envio = serializers.SerializerMethodField()
    domicilio_remitente = serializers.SerializerMethodField()

    def _get_foto_or_null(self, foto_obj):
        try:
            url = foto_obj.url
        except:
            return ''
        else:
            request = self.context.get('request')
            photo_url = foto_obj.url
            return request.build_absolute_uri(photo_url)

    def get_nro_pedido(self, obj):
        return obj.nro_pedido

    def get_usuario(self, obj):
        return obj.usuario_comprador.username

    def get_marca(self, obj):
        return obj.marca.nombre

    def get_cantidad_articulos(self, obj):
        qs_lineas_pedido = LineaPedido.objects.filter(pedido=obj)
        cantidad_articulos = 0
        for linea in qs_lineas_pedido:
            cantidad_articulos += linea.cantidad
        return cantidad_articulos

    def get_voucher_aplicado(self, obj):
        if obj.voucher_aplicado:
            return obj.voucher_aplicado.cod_voucher
        else:
            return None

    def get_estado_pedido(self, obj):
        return obj.get_estado_pedido_display()

    def get_cargo_costo_envio(self, obj):
        return obj.get_cargo_costo_envio_display()

    def get_email_destinatario(self, obj):
        if obj.flag_regalo:
            email_destinatario = obj.usuario_receptor_regalo.email 
        else:
            email_destinatario = obj.usuario_comprador.email 
        return email_destinatario

    def get_lineas_pedido(self, obj):
        lineas_pedido = []
        qs_lineas = LineaPedido.objects.filter(pedido=obj)
        for linea in qs_lineas:
            linea_dict = {'articulo_id': linea.articulo.pk,
                          'nombre_producto': linea.articulo.producto.nombre_producto,
                          'cod_producto': linea.articulo.producto.cod_producto,
                          'foto_principal': self._get_foto_or_null(linea.articulo.producto.foto_principal),
                          'talle': linea.articulo.talle,
                          'color': linea.articulo.producto.color,
                          'cantidad': linea.cantidad,
                          'precio': linea.precio}
            lineas_pedido.append(linea_dict)
        
        return lineas_pedido

    def get_responsable_envio(self, obj):
        return obj.get_responsable_envio_display() 

    def get_domicilio_remitente(self, obj):
        deposito_obj = obj.deposito_marca
        if deposito_obj:
            return DepositoSerializer(instance=deposito_obj).data
        else:
            return None
            
    def get_comision_vindu(self, obj):
        return obj.comision_vindu
    
    def get_domicilio_envio(self, obj):
        domicilio_temp = Domicilio(
            id = None,
            usuario_comprador = obj.usuario_comprador,
            nombre = obj.env_nombre,
            apellido = obj.env_apellido,
            calle = obj.env_calle,
            numero = obj.env_numero,
            piso = obj.env_piso,
            departamento = obj.env_departamento,
            provincia = obj.env_provincia,
            localidad_ref = obj.env_localidad_ref,
            cod_postal = obj.env_cod_postal
        )

        domicilio_env_ser = DomicilioDisplaySerializer(domicilio_temp, many=False, context={'request': self.context.get('request')})
        return domicilio_env_ser.data

    def get_domicilio_facturacion(self, obj):
        domicilio_temp = Domicilio(
            id = None,
            usuario_comprador = obj.usuario_comprador,
            nombre = obj.fac_nombre,
            apellido = obj.fac_apellido,
            calle = obj.fac_calle,
            numero = obj.fac_numero,
            piso = obj.fac_piso,
            departamento = obj.fac_departamento,
            provincia = obj.fac_provincia,
            localidad_ref = obj.fac_localidad_ref,
            cod_postal = obj.fac_cod_postal
        )

        domicilio_fac_ser = DomicilioDisplaySerializer(domicilio_temp, many=False, context={'request': self.context.get('request')})
        return domicilio_fac_ser.data

    class Meta:
        model = Pedido
        fields = ('nro_pedido', 'marca', 'usuario', 'importe_pedido', 'importe_descuentos', 'descuentos', 'importe_total', 
                  'cantidad_articulos', 'estado_pedido', 'fecha_pedido', 'comision_vindu', 'voucher_aplicado', 'domicilio_remitente',
                  'domicilio_envio', 'entre_1', 'entre_2', 'telefono_contacto', 'fecha_solicitada_entrega', 'comentarios_pedido',
                  'email_destinatario', 'cargo_costo_envio', 'costo_envio', 'domicilio_facturacion', 'lineas_pedido',
                  'responsable_envio', 'iflow_tracking_id', 'iflow_cod_etiqueta', 'iflow_print_url') 


class DomicilioInputSerializer(serializers.ModelSerializer):
    usuario_comprador = UserCompradorUsernameSerializer(read_only=True, many=False)
    nombre = serializers.CharField(required=True)
    apellido = serializers.CharField(required=True)
    calle = serializers.CharField(required=True)
    numero = serializers.CharField(required=True)
    piso = serializers.CharField(required=False,)   
    departamento = serializers.CharField(required=False)
    provincia = serializers.CharField(required=True)
    localidad_id = serializers.IntegerField(required=True)
    cod_postal = serializers.IntegerField(required=True)

    class Meta:
        model = Domicilio
        fields = ('id', 'usuario_comprador', 'nombre', 'apellido', 'calle', 'numero', 'piso', 'departamento',
                'provincia', 'localidad_id', 'cod_postal') 

    def validate_cod_postal(self, cod_postal):
        try:
            cod_postal_zona_obj = CodigoPostal.objects.get(cod_postal=cod_postal)
        except:
            raise serializers.ValidationError("Código postal inválido o inexistente")
        self.cod_postal_zona_obj = cod_postal_zona_obj 
        return cod_postal 

    def validate_localidad_id(self, localidad_id):
        try:
            localidad_obj = ProvinciaLocalidadZonaTarifa.objects.get(pk=localidad_id)
        except:
            raise serializers.ValidationError("Localidad inválida o inexistente")
        self.localidad_obj = localidad_obj 
        return localidad_id

    def create(self, validated_data):
        cod_postal = validated_data.pop('cod_postal')
        localidad_id = validated_data.pop('localidad_id')
        #print('validated_data: ', validated_data)
        
        # Validacion cruzada: el codigo postal de la localidad debe ser el mismo que el informado
        if self.localidad_obj.cod_postal_provincia.cod_postal != self.cod_postal_zona_obj.cod_postal:
            raise serializers.ValidationError("El código postal no corresponde a la localidad")            

        domicilio_obj = Domicilio.objects.create(cod_postal=self.cod_postal_zona_obj, localidad_ref=self.localidad_obj, **validated_data)
        return domicilio_obj


class SetDomicilioEnvioSerializer(serializers.Serializer):
    domicilio_envio_id = serializers.IntegerField(required=True)

class SetDatosAdicionalesEnvioSerializer(serializers.Serializer):
    #localidad_id = serializers.IntegerField(required=True)
    entre_1 = serializers.CharField(max_length=50, required=True)
    entre_2 = serializers.CharField(max_length=50, required=False)
    telefono_contacto = serializers.CharField(required=True, min_length=8, max_length=25)
    # Formato de fechas de Output y de Input: AAAA-MM-DD
    # fecha_solicitada_entrega = serializers.DateField(format=api_settings.DATE_FORMAT, input_formats=None, required=True)
    comentarios_pedido = serializers.CharField(max_length=150, allow_blank=True, trim_whitespace=False, required=False)


class SetDomicilioFacturacionSerializer(serializers.Serializer):
    domicilio_facturacion_id = serializers.IntegerField(required=True)


class SetVoucherSerializer(serializers.Serializer):
    cod_voucher = serializers.CharField(required=True)


class DisplayPagoPedidoSerializer(PedidoSerializer):
    url_pago_MP = serializers.URLField(read_only=True)
    url_pago_PU = serializers.URLField(read_only=True)

    class Meta:
        model = Pedido
        fields = ('nro_pedido', 'marca', 'proveedor_pago', 'usuario', 'importe_pedido', 'importe_descuentos', 'descuentos', 'importe_total', 
                  'cantidad_articulos', 'estado_pedido', 'fecha_pedido', 'comision_vindu', 'voucher_aplicado', 'domicilio_remitente',
                  'domicilio_envio', 'entre_1', 'entre_2', 'telefono_contacto', 'fecha_solicitada_entrega', 'comentarios_pedido',
                  'email_destinatario', 'cargo_costo_envio', 'costo_envio', 'domicilio_facturacion', 'lineas_pedido',
                  'responsable_envio', 'iflow_tracking_id', 'iflow_cod_etiqueta', 'iflow_print_url', 'url_pago_MP', 'url_pago_PU') 
