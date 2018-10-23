# -*- encoding: utf-8 -*-
#from carton.cart import Cart
from rest_framework.permissions import (AllowAny, IsAuthenticated)
from rest_framework import permissions, status, viewsets, exceptions, views, generics
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from mercado_vindu.models import TalleProducto
from .models import *
from decimal import *
from auth_api.models import UserComprador
from configuraciones.models import DescuentoPrimeraCompra, CodigoPostal, ProvinciaLocalidadZonaTarifa, Voucher
from django.conf import settings
from django.db.models import ProtectedError
import requests
import mercadopago
from django.core.urlresolvers import reverse
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from auth_api.authentication import BearerTokenAuthentication
from datetime import timedelta, datetime
from django.utils import timezone
import hashlib
#import json
#import simplejson


class GetCarritoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    serializer_class = CarritoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'put', 'head']

    def get_queryset(self):
        """
        Esta vista retorna el carrito del usuario 
        """
        try:
            usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
        except:
            return []

        cart, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)

        return [cart]


    def update(self, request, format=None, *args, **kwargs):
        """
        Vacía el carrito del usuario 
        """
        try:
            carrito_obj = Carrito.objects.get(usuario_comprador__username=request.user.username)
        except:
            pass
        else:
            carrito_obj.delete()

        try:
            usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
        except:
            return Response({"error": 'Usuario Comprador inválido o inexistente'}, status=status.HTTP_400_BAD_REQUEST)

        cart, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)
        ser = CarritoSerializer(cart, context={'request': request})
        return Response(ser.data)

class AgregarArticuloViewSet(APIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    serializer_class = AgregarArticuloSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def validate(self, carrito, articulo, cantidad):
        cart = carrito

        # Se valida que los artículos del carrito pertenezcan a la misma marca
        if not carrito.is_empty:
            lista_articulos = carrito.products
            primer_articulo = lista_articulos[0]    
            marca_primer_articulo = primer_articulo.producto.marca

            if marca_primer_articulo != articulo.producto.marca:
                message = "No se puede combinar artículos de distintas marcas en un mismo carrito"
                return False, message                        

        # Validaciones de cantidad y stock
        cantidad = int(cantidad)
        if cantidad <= 0:
            message = "La cantidad debe ser mayor que cero"
            return False, message

        if articulo in cart.products:
            nueva_cantidad = cart._items_dict[articulo.pk].cantidad + cantidad
        else:
            nueva_cantidad = cantidad

        if articulo.stock < nueva_cantidad:
            message = "No hay suficiente stock para agregar el artículo"
            return False, message

        return True, None


    def post(self, request, format=None, *args, **kwargs):
        p_ser = AgregarArticuloSerializer(data=request.data, context={'request': request})
        if p_ser.is_valid():
            try:
                usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
            except:
                return Response({"error": 'Usuario Comprador inválido o inexistente'}, status=status.HTTP_400_BAD_REQUEST)

            carrito, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)

            articulo_id = p_ser.validated_data['articulo_id']
            cantidad = p_ser.validated_data['cantidad']

            try:
                talle_obj = TalleProducto.objects.get(pk=articulo_id)
            except:
                return Response({"error": "Artículo inexistente"}, status=status.HTTP_404_NOT_FOUND)        

            carrito_valido, message = self.validate(carrito, talle_obj, cantidad)
            if not carrito_valido:
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

            carrito.add(talle_obj, cantidad)   
    
            ser = CarritoSerializer(
                carrito, context={'request': request})
            return Response(ser.data)

        return Response(p_ser.errors, status=status.HTTP_406_NOT_ACCEPTABLE)

class CarritoDetalleViewSet(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CarritoDetalleSerializer
    http_method_names = ['get', 'put', 'delete']

    def update(self, request, format=None, *args, **kwargs):
        p_ser = CarritoDetalleSerializer(data=request.data, context={'request': request})
        if p_ser.is_valid():
            try:
                usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
            except:
                return Response({"error": 'Usuario Comprador inválido o inexistente'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                articulo_id = kwargs.get('articulo_id')
                talle_obj = TalleProducto.objects.get(pk=articulo_id)
            except:
                talle_obj = None

            if talle_obj:
                cart, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)
                if not talle_obj in cart.products:
                    return Response({"error": "El artículo no está en el carrito"}, status=status.HTTP_404_NOT_FOUND)                   
                else: # el artículo está en el carrito, se valida que haya suficiente stock para la nueva cantidad
                    cantidad = p_ser.validated_data['cantidad']
                    if talle_obj.stock < cantidad:
                        return Response({"error": "No hay suficiente stock para agregar el artículo"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        cart.set_quantity(talle_obj, cantidad)
                        ser = CarritoSerializer(cart, context={'request': request})
                        return Response(ser.data)

            else:
                return Response({"error": "Artículo inválido o inexistente"}, status=status.HTTP_404_NOT_FOUND)                   

        else:
            return Response({"error": "Cantidad inválida o no informada"}, status=status.HTTP_400_BAD_REQUEST)


    def destroy(self, request, format=None, *args, **kwargs):
        try:
            articulo_id = kwargs.get('articulo_id')
            talle_obj = TalleProducto.objects.get(pk=articulo_id)
        except:
            talle_obj = None

        try:
            usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
        except:
            return Response({"error": 'Usuario Comprador inválido o inexistente'}, status=status.HTTP_400_BAD_REQUEST)


        if talle_obj:
            cart, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)
            if not talle_obj in cart.products:
                return Response({"error": "El artículo no está en el carrito"}, status=status.HTTP_404_NOT_FOUND)                   
            else: # el artículo está en el carrito
                cart.remove(talle_obj)
                ser = CarritoSerializer(cart, context={'request': request})
                return Response(ser.data)

        else:
            return Response({"error": "Artículo inválido o inexistente"}, status=status.HTTP_404_NOT_FOUND)                   


class CheckoutCarritoViewSet(APIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['post']

    def post(self, request, format=None, *args, **kwargs):
        # Se valida que el carrito no esté vacío
        try:
            usuario_comprador_obj = UserComprador.objects.get(username=self.request.user.username)
        except:
            return Response({"error": "Usuario comprador inválido o inexistente"}, status=status.HTTP_400_BAD_REQUEST)


        carrito, created = Carrito.objects.get_or_create(usuario_comprador=usuario_comprador_obj)

        if carrito.is_empty:
            return Response({"error": "Checkout inválido, el carrito está vacío"}, status=status.HTTP_400_BAD_REQUEST)

        # Se blanquean datos cargados anteriormente por si el usuario volvió atras y editó el carrito:
        carrito.importe_descuentos = 0
        carrito.importe_dto_primera_compra = 0
        carrito.voucher_aplicado = None
        carrito.domicilio_envio = None
        carrito.entre_1 = None
        carrito.entre_2 = None
        carrito.telefono_contacto = None
        carrito.comentarios_pedido = None
        carrito.zona_tarifa = None
        carrito.costo_envio = 0
        carrito.domicilio_facturacion = None
        carrito.save()


        # Por cada artículo en el carrito se verifica que exista stock suficiente para generar el Pedido
        lista_articulos = carrito.items
        for articulo_carrito in lista_articulos:
            articulo_pk = articulo_carrito.articulo.id
            # Se accede de nuevo a la base para obtener la cantidad actualizada de stock y no la
            # obtenga del cache de la BD
            articulo_bd = TalleProducto.objects.get(pk=articulo_pk)
            if articulo_bd.stock < articulo_carrito.cantidad:
                msg = "Cantidad insuficiente de stock para el articulo: "
                msg += articulo_carrito.articulo.producto.nombre_producto
                return Response({"error":  msg }, status=status.HTTP_400_BAD_REQUEST)

        # Controla que los precios de los items del carrito sean los vigentes, si no los actualiza
        # Esta lógica se saca pq no se guardan ahora los precios en el carrito
        '''
        for item in carrito.items:
            precio_actual_articulo = item.articulo.producto.get_precio_actual()
            if item.precio != precio_actual_articulo:
                item.precio = precio_actual_articulo
                linea_carrito_obj = carrito._items_dict[item.articulo.pk] 
                linea_carrito_obj.precio = precio_actual_articulo
                linea_carrito_obj.save()
        '''        

        try:
            user_comprador = UserComprador.objects.get(username=request.user.username)
        except:
            return Response({"error": "Usuario comprador inválido"}, status=status.HTTP_400_BAD_REQUEST)


        importe_descuentos = 0

        # Verificación y cálculo de descuento por primera compra
        # - Primero se verifica si el usuario hizo alguna compra
        list_estados_pagados = ['P', 'E']
        qs_cant_compras = Pedido.objects.filter(usuario_comprador=user_comprador, estado_pedido__in=list_estados_pagados).count()  
        # - Luego se verifica si el comprador califica para el descuento
        if qs_cant_compras == 0:
            desc_primera_compra_obj = DescuentoPrimeraCompra.objects.get()
            importe_descuento_primera_compra = desc_primera_compra_obj.descuento_primera_compra(user_comprador)
        else:
            importe_descuento_primera_compra = 0  
        importe_descuentos += importe_descuento_primera_compra    

        # Se completan datos calculados en el modelo Carrito:
        # En esta instancia el importe_descuentos = importe_descuento_primera_compra
        carrito.importe_dto_primera_compra = importe_descuento_primera_compra
        carrito.importe_descuentos = importe_descuentos
        carrito.save()


        # Serializa el pedido para mostrarlo en el Response
        ser = CarritoSerializer(
            carrito, context={'request': request})
        return Response(ser.data)


class GetDomiciliosViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Domicilio.objects.all()
    serializer_class = DomicilioDisplaySerializer
    http_method_names = ['get']


    def get_queryset(self):
        """
        Esta vista retorna los domicilios del usuario logueado
        """

        username_auth = self.request.user.username

        if username_auth:
            try:
                usuario_obj = UserComprador.objects.get(username=username_auth)
            except:
                queryset = []
            else:
                queryset = self.queryset.filter(usuario_comprador=usuario_obj).order_by('pk')

        return queryset

class AgregarDomicilioViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Domicilio.objects.all()
    serializer_class = DomicilioInputSerializer
    http_method_names = ['get', 'post']


    def create(self, request, format=None, *args, **kwargs):
        datos_request = request.data
        try:
            usuario_comprador = UserComprador.objects.get(username=request.user.username)
        except:
            return Response({"error": "Usuario comprador inválido o inexistente"}, status=status.HTTP_400_BAD_REQUEST)

        #datos_request['usuario_comprador'] = usuario_comprador
        p_ser = DomicilioInputSerializer(data=datos_request, context={'request': request})

        if p_ser.is_valid():
            dict = p_ser.validated_data
            #print('dict: ', dict)
            nuevo_domicilio = p_ser.save(usuario_comprador=usuario_comprador)

            #qs_domicilios = Domicilio.objects.filter(usuario_comprador=request.user).order_by('pk')
            domicilio_ser = DomicilioDisplaySerializer(nuevo_domicilio, context={'request': request})
            return Response(domicilio_ser.data)      

        else:
            return Response(p_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class DomicilioViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Domicilio.objects.all()
    lookup_url_kwarg = "domicilio_id"
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        try:
            domicilio_id = kwargs.get('domicilio_id')
        except:
            return Response({'error': 'Falta el domicilio_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            domicilio_obj = Domicilio.objects.get(pk=domicilio_id)
        except:
            return Response({'error': 'Domicilio inexistente'}, status=status.HTTP_404_NOT_FOUND)

        username_auth = request.user.username

        if domicilio_obj.usuario_comprador.username != username_auth:
            return Response({'error': 'El domicilio no pertenece al usuario logueado'}, status=status.HTTP_400_BAD_REQUEST)

        attrs = {'username': username_auth , 'domicilio_id': domicilio_id}

        try:
            domicilio_obj.delete()
        except ProtectedError as exception:
            return Response({'error': 'El domicilio está siendo usando en al menos un pedido'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(attrs, status=status.HTTP_204_NO_CONTENT)



class SetDomicilioEnvioViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    http_method_names = ['get', 'put']


    def determinar_pagador_envio(self, carrito_obj, request, *args, **kwargs):
        marca = carrito_obj.get_marca()
        importe_promocion_envio = marca.valor_promocion_envio

        if importe_promocion_envio > 0 and carrito_obj.total >= importe_promocion_envio:
            pagador = 'M' # Paga la Marca
        else:
            pagador = 'A' # Paga Anting con cargo al comprador

        return pagador


    def calcular_costo_envio(self, carrito_obj, localidad_envio, request, *args, **kwargs):
        zona_tarifa_obj = localidad_envio.zona_tarifa

        # TODO: ACA SE SUPONE QUE EL PAQUETE DE ENVIO TIENE UN PESO HASTA 3 KG - REVISAR !!!!!
        costo_envio = zona_tarifa_obj.tarifa_hasta_3
        return costo_envio


    def update(self, request, format=None, *args, **kwargs):
        p_ser = SetDomicilioEnvioSerializer(data=request.data, context={'request': request})

        if p_ser.is_valid():
            usuario_comprador = UserComprador.objects.get(username=request.user.username)   

            try:
                carrito_obj = Carrito.objects.get(usuario_comprador=usuario_comprador)
            except:
                return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)                   

            ''' # REVISAR ESTA LOGICA CUANDO SE DESARROLLEN REGALOS
            if not pedido_obj.flag_regalo:
                if usuario_comprador != pedido_obj.usuario_comprador:
                    return Response({"error": "El nro de pedido no corresponde al usuario"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if usuario_comprador != pedido_obj.usuario_receptor:
                    return Response({"error": "Usuario sin permiso sobre el pedido"}, status=status.HTTP_400_BAD_REQUEST)
            '''

            domicilio_envio_id = p_ser.validated_data['domicilio_envio_id']
            try:
                domicilio_envio = Domicilio.objects.get(pk=domicilio_envio_id)
            except:
                return Response({"error": "Id de domicilio no encontrado"}, status=status.HTTP_404_NOT_FOUND)                   


            localidad_obj = domicilio_envio.localidad_ref

            # Función para deteminar quién paga el costo del envío
            pagador = self.determinar_pagador_envio(carrito_obj, request, *args, **kwargs)

            # Función para calcular el costo del envío y deteminar quién lo paga
            costo_envio = self.calcular_costo_envio(carrito_obj, localidad_obj, request, *args, **kwargs)

            carrito_obj.domicilio_envio = domicilio_envio

            carrito_obj.costo_envio = costo_envio
            carrito_obj.cargo_costo_envio = pagador
            carrito_obj.zona_tarifa = localidad_obj

            carrito_obj.save()
            carrito_ser = CarritoSerializer(carrito_obj, context={'request': request})
            return Response(carrito_ser.data)  

        else:
            return Response(p_ser.errors, status=status.HTTP_400_BAD_REQUEST)

class SetDatosAdicionalesEnvioViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Pedido.objects.all()
    serializer_class = CarritoSerializer
    http_method_names = ['get', 'put']


    def update(self, request, format=None, *args, **kwargs):
        p_ser = SetDatosAdicionalesEnvioSerializer(data=request.data, context={'request': request})

        if p_ser.is_valid():
            usuario_comprador = UserComprador.objects.get(username=request.user.username)   

            try:
                carrito_obj = Carrito.objects.get(usuario_comprador=usuario_comprador)
            except:
                return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)                   

            ''' ### REVISAR ESTA LOGICA PARA EL CASO DE REGALOS
            if not pedido_obj.flag_regalo:
                if usuario_comprador != pedido_obj.usuario_comprador:
                    return Response({"error": "El nro de pedido no corresponde al usuario"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                if usuario_comprador != pedido_obj.usuario_receptor:
                    return Response({"error": "Usuario sin permiso sobre el pedido"}, status=status.HTTP_400_BAD_REQUEST)
            '''

            if not carrito_obj.domicilio_envio:
                return Response({"error": "Domicilio de envío no informado"}, status=status.HTTP_400_BAD_REQUEST)


            telefono_contacto = p_ser.validated_data['telefono_contacto']
            carrito_obj.telefono_contacto = telefono_contacto
            carrito_obj.entre_1 = p_ser.validated_data['entre_1']
            try:
                carrito_obj.entre_2 = p_ser.validated_data['entre_2']
            except:
                carrito_obj.entre_2 = None

            try:
                carrito_obj.comentarios_pedido = p_ser.validated_data['comentarios_pedido']
            except:
                carrito_obj.comentarios_pedido = ''

            carrito_obj.save()
            carrito_ser = CarritoSerializer(carrito_obj, context={'request': request})
            return Response(carrito_ser.data)  

        else:
            return Response(p_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class SetDomicilioFacturacionViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    http_method_names = ['get', 'put']


    def update(self, request, format=None, *args, **kwargs):
        p_ser = SetDomicilioFacturacionSerializer(data=request.data, context={'request': request})

        if p_ser.is_valid():
            usuario_comprador = UserComprador.objects.get(username=request.user.username)   

            ## REVISAR ESTA LOGICA CUANDO SE DESAROLLE REGALOS
            try:
                carrito_obj = Carrito.objects.get(usuario_comprador=usuario_comprador)
            except:
                return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)                   


            domicilio_facturacion_id = p_ser.validated_data['domicilio_facturacion_id']
            try:
                domicilio_facturacion = Domicilio.objects.get(pk=domicilio_facturacion_id)
            except:
                return Response({"error": "Id de domicilio no encontrado"}, status=status.HTTP_404_NOT_FOUND)                   

            carrito_obj.domicilio_facturacion = domicilio_facturacion
            carrito_obj.save()
            carrito_ser = CarritoSerializer(carrito_obj, context={'request': request})
            return Response(carrito_ser.data)  

        else:
            return Response(p_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class SetVoucherViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Carrito.objects.all()
    serializer_class = SetVoucherSerializer
    http_method_names = ['get', 'put']


    def update(self, request, format=None, *args, **kwargs):
        p_ser = SetVoucherSerializer(data=request.data, context={'request': request})

        if p_ser.is_valid():
            usuario_comprador = UserComprador.objects.get(username=request.user.username)   

            ## REVISAR ESTA LOGICA CUANDO SE DESAROLLE REGALOS
            try:
                carrito_obj = Carrito.objects.get(usuario_comprador=usuario_comprador)
            except:
                return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)                   
            
            cod_voucher = p_ser.validated_data['cod_voucher']
            try:
                voucher_obj = Voucher.objects.get(cod_voucher=cod_voucher)
            except:
                return Response({"error": "Voucher no encontrado"}, status=status.HTTP_404_NOT_FOUND)  

            flag_voucher_valido, mensaje = voucher_obj.check_voucher_aplicable(carrito_obj)    
            if not flag_voucher_valido:
                return Response({"error": mensaje}, status=status.HTTP_400_BAD_REQUEST)   

            # Se aplica el Voucher
            carrito_obj.voucher_aplicado = voucher_obj
            carrito_obj.importe_descuentos += voucher_obj.importe_voucher
            #pedido_obj.importe_total = pedido_obj.importe_pedido - pedido_obj.importe_descuentos

            carrito_obj.save()


            carrito_ser = CarritoSerializer(carrito_obj, context={'request': request})
            return Response(carrito_ser.data)  

        else:
            return Response(p_ser.errors, status=status.HTTP_400_BAD_REQUEST)



class GetPedidosViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    serializer_class = PedidoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        try:
            usuario_comprador = UserComprador.objects.get(username=self.request.user.username)
        except:
            qs_pedidos = []
        else:
            qs_pedidos = Pedido.objects.filter(usuario_comprador=usuario_comprador).order_by('-fecha_pedido')

        return qs_pedidos

class DetallePedidoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    serializer_class = PedidoSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Pedido.objects.all()
    http_method_names = ['get', 'head']


    def get_queryset(self):
        nro_pedido = self.kwargs['nro_pedido']

        if nro_pedido is not None:
            queryset = self.queryset.filter(pk=nro_pedido)

            try:
                pedido_obj = Pedido.objects.get(pk=nro_pedido)
            except:
                raise exceptions.NotFound(detail="Nro de Pedido no encontrado")

            else:
                # Se verifica si el pedido corresponde al usuario logueado
                user = self.request.user
                if user.username != pedido_obj.usuario_comprador.username:
                    raise exceptions.ValidationError(detail="El Pedido no corresponde al usuario logueado")
        else:
            raise exceptions.NotFound(detail="Nro de Pedido no encontrado")

        return [pedido_obj]


class PagarPedidoViewSet(viewsets.ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Carrito.objects.all()
    http_method_names = ['get', 'put']

    def _get_foto_or_null(self, foto_obj, request):
        try:
            url = foto_obj.url
        except:
            return ''
        else:
            photo_url = foto_obj.url
            return request.build_absolute_uri(photo_url)

    def procesar_pago_MP(self, request, pedido_obj):
        nro_pedido = pedido_obj.nro_pedido
        # TODO: en desarrollo protocolo es http. En producción debe ser https. Cambiar en settings
        #ipn_url = 'https://' + settings.DOMAIN + reverse(url_name, kwargs={'external_reference': external_reference})
        ipn_url = settings.MP_PROTOCOLO + settings.DOMAIN + reverse('pagos:ipn_argentina', kwargs={'external_reference': nro_pedido})

        print('ipn_url: ', ipn_url)
        lineas_pedido = []
        qs_lineas = LineaPedido.objects.filter(pedido=pedido_obj)
        for linea in qs_lineas:
            producto_obj = linea.articulo.producto
            linea_dict = {'id': linea.articulo.pk,
                          'title': producto_obj.nombre_producto,
                          'description': producto_obj.descripcion,
                          'quantity': linea.cantidad,
                          'unit_price': float(linea.precio),
                          'currency_id': 'ARS',
                          'picture_url': self._get_foto_or_null(producto_obj.foto_principal_thumb, request),
                          }
            lineas_pedido.append(linea_dict)

        # Si existe algun descuento (por primera compra o voucher, se agrega como otra línea del pedido)
        qs_descuentos = Descuento.objects.filter(pedido=pedido_obj)
        if qs_descuentos:
            descuento_obj = qs_descuentos[0]
            linea_dict = {'id': 0,
                          'title': 'Descuento Vindu',
                          'description': descuento_obj.motivo_descuento,
                          'quantity': 1,
                          'unit_price': float(descuento_obj.importe_descuento) * -1,
                          'currency_id': 'ARS',
                          'picture_url': '',
                           }
            lineas_pedido.append(linea_dict)

        # Si se debe cobrar el costo de envío al comprador, se agrega otra línea al pedido
        if pedido_obj.cargo_costo_envio == 'A' and pedido_obj.costo_envio > 0:
            linea_dict = {'id': 0,
                          'title': 'Costo de envío',
                          'description': 'Cargo por costo de envío',
                          'quantity': 1,
                          'unit_price': float(pedido_obj.costo_envio),
                          'currency_id': 'ARS',
                          'picture_url': '',
                           }
            lineas_pedido.append(linea_dict)

        protocolo_dominio = 'https://' + settings.DOMAIN

        preference = {
            "items": lineas_pedido,
            "external_reference": nro_pedido,
            "notification_url": ipn_url,
            "back_urls": {
                "success": protocolo_dominio + "/pagos/mercadopago/pago-exitoso/?p=" + str(nro_pedido),
                "failure": protocolo_dominio + "/pagos/mercadopago/pago-erroneo/",
                "pending": protocolo_dominio + "/pagos/mercadopago/pago-pendiente/"
            },
            "auto_return": "approved",
        }
        marca_obj = pedido_obj.marca

        # Autenticación en MP con las credenciales del seller
        try:
            mp = mercadopago.MP(marca_obj.mp_client_id, marca_obj.mp_client_secret)  # seller credentials
        except:
            return Response({"error": "error en credenciales del vendedor - auth"}, status=status.HTTP_400_BAD_REQUEST) 

        try:
            preferenceResult = mp.create_preference(preference)
        except:
            return Response({"error": "error en credenciales del vendedor - create_preference"}, status=status.HTTP_400_BAD_REQUEST) 

        try:
            url = preferenceResult["response"]["init_point"]
        except:
            return Response({"error": "error en url de redirección pago"}, status=status.HTTP_400_BAD_REQUEST) 
            #url = reverse('pagos:mp_pago_erroneo')
        else:
            print('respuesta de MP, preferenceResult: ', preferenceResult)
            print('respuesta de MP, url             : ', url) 
            pedido_obj.url_pago_MP = url  
            pedido_obj.save()
            pedido_ser = DisplayPagoPedidoSerializer(pedido_obj, context={'request': request})
            return Response(pedido_ser.data)  


    def procesar_pago_PAYU(self, request, pedido_obj):
        marca = pedido_obj.marca
        merchand_id = str(marca.pu_merchand_id)
        account_id  = str(marca.pu_account_id)
        description = "Compra por Vindu"
        referenceCode = 'Pedido Nro ' + str(pedido_obj.nro_pedido)
        amount = str(pedido_obj.importe_total)
        tax = '0'
        taxReturnBase = '0'
        currency = 'ARS'
        api_key = marca.pu_api_key

        string_to_hash = api_key + '~' + merchand_id + '~' + referenceCode + '~' + amount + '~' + currency
        print('string_to_hash: ', string_to_hash)
        signature = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

        if settings.URL_PAYU_TEST:
            payu_url  = settings.URL_PAYU_SANDBOX
            test = '1'
        else:
            payu_url  = settings.URL_PAYU_PRODUCTION
            test = '0'

        buyerEmail = pedido_obj.usuario_comprador.email
        responseUrl = 'http://www.test.com/response'
        confirmationUrl = 'http://www.test.com/confirmation'


        data = {}
        data['merchandId'] = merchand_id
        data['accountId']  = account_id
        data['description'] = description
        data['referenceCode'] = referenceCode
        data['amount'] = amount
        data['tax'] = tax
        data['taxReturnBase'] = taxReturnBase
        data['currency'] = currency
        data['signature'] = signature
        data['test'] = test
        data['buyerEmail'] = buyerEmail
        data['responseUrl'] = responseUrl
        data['confirmationUrl'] = confirmationUrl

        print('data - post - payu: ', data)

        response = requests.post(payu_url, data = json.dumps(data))

        pedido_obj.url_pago_PU = response.url  
        pedido_obj.save()
        pedido_ser = DisplayPagoPedidoSerializer(pedido_obj, context={'request': request})
        return Response(pedido_ser.data)  

    def crear_pedido(self, carrito_obj):
        marca = carrito_obj.get_marca()

        # Se calcula la comisión Vindu
        porc_comision_vindu = marca.porcentaje_vindu
        importe_comision_vindu = carrito_obj.total * porc_comision_vindu * Decimal('0.01')

        # Domicilio de envio:
        dom_envio = carrito_obj.domicilio_envio
        # Domicilio de facturacion:
        dom_fact = carrito_obj.domicilio_facturacion

        nuevo_pedido = Pedido(
            marca = marca,
            proveedor_pago = marca.proveedor_pago,  
            usuario_comprador = carrito_obj.usuario_comprador,
            importe_descuentos = carrito_obj.importe_descuentos,          
            estado_pedido = 'I',
            comision_vindu = importe_comision_vindu,
            voucher_aplicado = carrito_obj.voucher_aplicado,
            flag_regalo = carrito_obj.flag_regalo,
            deposito_marca = carrito_obj.deposito_marca,
            usuario_receptor_regalo = carrito_obj.usuario_receptor_regalo,
            # Datos del domicilio de envio planchados:
            env_nombre = dom_envio.nombre,
            env_apellido = dom_envio.apellido,
            env_calle = dom_envio.calle,
            env_numero = dom_envio.numero,
            env_piso = dom_envio.piso,
            env_departamento = dom_envio.departamento,
            env_provincia = dom_envio.provincia,
            env_localidad_ref = dom_envio.localidad_ref,
            env_cod_postal = dom_envio.cod_postal,
            entre_1 = carrito_obj.entre_1,
            entre_2 = carrito_obj.entre_2,
            telefono_contacto = carrito_obj.telefono_contacto,
            comentarios_pedido = carrito_obj.comentarios_pedido,
            zona_tarifa = carrito_obj.zona_tarifa,
            cargo_costo_envio = carrito_obj.cargo_costo_envio,
            costo_envio = carrito_obj.costo_envio,
            responsable_envio = carrito_obj.responsable_envio,
            # Datos del domicilio de facturación planchados:
            fac_nombre = dom_fact.nombre,
            fac_apellido = dom_fact.apellido,
            fac_calle = dom_fact.calle,
            fac_numero = dom_fact.numero,
            fac_piso = dom_fact.piso,
            fac_departamento = dom_fact.departamento,
            fac_provincia = dom_fact.provincia,
            fac_localidad_ref = dom_fact.localidad_ref,
            fac_cod_postal = dom_fact.cod_postal
        )

        nuevo_pedido.save()

        # Por cada descuento, se crea una entrada en la tabla de descuentos:
        voucher_obj = nuevo_pedido.voucher_aplicado
        if voucher_obj:
            nuevo_descuento = Descuento(
                pedido = nuevo_pedido,
                motivo_descuento = "Voucher: " + voucher_obj.cod_voucher,
                importe_descuento = voucher_obj.importe_voucher
            )
            nuevo_descuento.save()

        importe_descuento_primera_compra = carrito_obj.importe_dto_primera_compra
        if importe_descuento_primera_compra > 0:
            nuevo_descuento = Descuento(
                pedido = nuevo_pedido,
                motivo_descuento = "Descuento Vindu por primera compra",
                importe_descuento = importe_descuento_primera_compra
            )
            nuevo_descuento.save()

        # Por cada artículo en el carrito se crea una entrada en la tabla LineaPedido
        lista_articulos = carrito_obj.items
        for linea_carrito in lista_articulos:
            linea_pedido = LineaPedido(
                pedido = nuevo_pedido,
                articulo = linea_carrito.articulo,
                cantidad = linea_carrito.cantidad,
                precio = linea_carrito.precio
            )
            linea_pedido.save()

        return nuevo_pedido


    def update(self, request, format=None, *args, **kwargs):
        usuario_comprador = UserComprador.objects.get(username=request.user.username)   

        ## REVISAR ESTA LOGICA CUANDO SE DESAROLLE REGALOS
        try:
            carrito_obj = Carrito.objects.get(usuario_comprador=usuario_comprador)
        except:
            return Response({"error": "Carrito vacío"}, status=status.HTTP_400_BAD_REQUEST)                   

        # El carrito debe tener fijados los domicilios de envío y de facturación y datos adicionales de envio
        if not carrito_obj.domicilio_envio:
            return Response({"error": "El pedido no tiene domicilio de envío"}, status=status.HTTP_400_BAD_REQUEST)

        if not carrito_obj.domicilio_facturacion:
            return Response({"error": "El pedido no tiene domicilio de facturación"}, status=status.HTTP_400_BAD_REQUEST)

        if not carrito_obj.entre_1 or not carrito_obj.telefono_contacto:
            return Response({"error": "Falta cargar datos adicionales al envío del pedido"}, status=status.HTTP_400_BAD_REQUEST)


        # Se genera el Pedido
        pedido_obj = self.crear_pedido(carrito_obj)   

        # Se vacía el carrito de compras - Se hace con delete y no con clear para eliminarlo completamente
        carrito_obj.delete()   
   


        proveedor_pago = pedido_obj.marca.proveedor_pago
        if proveedor_pago == 'MP':
            return self.procesar_pago_MP(request, pedido_obj)
        else:
            return self.procesar_pago_PAYU(request, pedido_obj)

