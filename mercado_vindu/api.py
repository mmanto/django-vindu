# -*- encoding: utf-8 -*-
import io
import csv

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import *
from auth_api.models import UserMarca, UserComprador
from .serializers import *
from rest_framework import permissions, status, viewsets, exceptions, views, generics
from rest_framework.decorators import api_view, detail_route, list_route
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from django.db.models import Q
from django.db.models.query import EmptyQuerySet
from wsgiref.util import FileWrapper
import datetime
from rest_framework.pagination import LimitOffsetPagination
from django.utils import timezone
from django.http import HttpResponse
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from auth_api.authentication import BearerTokenAuthentication


class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

class MarcaViewSet(ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

class ProductosAdminByMarcaCategoriaViewSet(ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductosAdminByMarcaCategoriaSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']

        if marca_id is not None:
            queryset = self.queryset.filter(marca_id=marca_id)
        else:
            queryset = self.queryset

        categoria_id = self.kwargs['categoria_id']
        if categoria_id is not None:
            queryset = queryset.filter(categoria_id=categoria_id)

        try:
            producto_id = self.kwargs['pk']
            queryset = queryset.exclude(pk=producto_id)
        except:
            producto_id = None
        return queryset

class ProductosCombAdminByMarcaCategoriaViewSet(ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductosAdminByMarcaCategoriaSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']

        if marca_id is not None:
            queryset = self.queryset.filter(marca_id=marca_id)
        else:
            queryset = self.queryset

        categoria_id = self.kwargs['categoria_id']
        if categoria_id is not None:
            queryset = queryset.exclude(categoria_id=categoria_id)

        try:
            producto_id = self.kwargs['pk']
            queryset = queryset.exclude(pk=producto_id)
        except:
            producto_id = None
        return queryset


class MarcaAllViewSet(ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = MarcaAllSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        return queryset


class FiltrosCategoriasMarcaViewSet(ModelViewSet):
    queryset = Marca.objects.all()
    serializer_class = FiltrosCategoriasMarcaSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        return queryset

class MarcaSeguidaViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = MarcaSeguida.objects.all()
    serializer_class = MarcaSeguidaSerializer
    lookup_url_kwarg = "marca_id"

    def get_queryset(self):
        """
        Esta vista retorna las marcas que sigue el usuario que está logueado
        """
        marca_id = self.kwargs.get(self.lookup_url_kwarg)

        try:
            producto_obj = marca_obj = Marca.objects.get(pk=marca_id)
        except:
            return Response({"error": "La marca no existe"}, status=status.HTTP_404_NOT_FOUND)

        user = self.request.user
        return self.queryset.filter(usuario=user, marca=marca_obj)

    def post(self, request, format=None, *args, **kwargs):
        marca_id = kwargs.get('marca_id')
        marca_obj = Marca.objects.get(pk=marca_id)
        user = request.user

        attrs = {'username': user.username , 'marca_id': marca_obj.id}
        if MarcaSeguida.objects.filter(usuario__pk=user.id, marca=marca_obj).exists():
            return Response({"error": "La marca ya está siendo seguida"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MarcaSeguidaSerializer(data=attrs)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        marca_id = kwargs.get('marca_id')
        marca_obj = Marca.objects.get(pk=marca_id)
        user = request.user
        attrs = {'username': user.username , 'marca_id': marca_obj.id}
        try:
            instance = MarcaSeguida.objects.get(usuario=user, marca=marca_obj)
            serializer = MarcaSeguidaSerializer(instance=instance,data=request.data)

            if serializer.is_valid():
                instance.delete()
                return Response(attrs, status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except MarcaSeguida.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class GetMarcasSeguidasViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = MarcaSeguida.objects.all()
    serializer_class = MarcaSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        user = self.request.user
        queryset_marcas = self.queryset.filter(usuario=user).values('marca')
        list_id_marcas = []
        for item_marca in queryset_marcas:
            list_id_marcas.append(item_marca['marca'])
        qs_marcas = Marca.objects.filter(pk__in=list_id_marcas)
        return qs_marcas

'''
class ProductoFavoritoViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProductoFavorito.objects.all()
    serializer_class = ProductoFavoritoSerializer
    lookup_url_kwarg = "producto_id"

    def get_queryset(self):
        """
        Esta vista retorna los productos favoritos del usuario que está logueado
        """
        producto_id = self.kwargs.get(self.lookup_url_kwarg)
        producto_obj = Producto.objects.get(pk=producto_id)
        user = self.request.user
        return self.queryset.filter(usuario=user, producto=producto_obj)

    def post(self, request, format=None, *args, **kwargs):
        producto_id = kwargs.get('producto_id')
        try:
            producto_obj = Producto.objects.get(pk=producto_id)
        except:
            return Response({"error": "El producto no existe"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        attrs = {'username': user.username , 'producto_id': producto_obj.id}
        if ProductoFavorito.objects.filter(usuario__pk=user.id, producto=producto_obj).exists():
            return Response({"error": "El producto ya es favorito"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductoFavoritoSerializer(data=attrs)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        producto_id = kwargs.get('producto_id')
        producto_obj = Producto.objects.get(pk=producto_id)
        user = request.user
        attrs = {'username': user.username , 'producto_id': producto_obj.id}
        try:
            instance = ProductoFavorito.objects.get(usuario=user, producto=producto_obj)
            serializer = ProductoFavoritoSerializer(instance=instance,data=request.data)

            if serializer.is_valid():
                instance.delete()
                return Response(attrs, status=status.HTTP_204_NO_CONTENT)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except MarcaSeguida.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
'''

class AgregarWishListViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = WishList.objects.all()
    serializer_class = WishListSerializer
    http_method_names = ['post']


    def create(self, request, format=None, *args, **kwargs):
        user = self.request.user
        id_articulo = kwargs.get('articulo_id')

        try:
            talle_obj = TalleProducto.objects.get(pk=id_articulo)
        except:
            return Response({"error": "Artículo inexistente"}, status=status.HTTP_404_NOT_FOUND)

        attrs = {'username': user.username , 'id_producto': talle_obj.producto.pk, 'nombre_producto': talle_obj.producto.nombre_producto, 'talle': talle_obj.talle}

        if WishList.objects.filter(usuario__pk=user.id, producto=talle_obj.producto, talle=talle_obj).exists():
            return Response({"error": "El producto ya está en el WishList"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario_obj = UserComprador.objects.get(username=user.username)
            wishlist_obj = WishList(usuario=usuario_obj, producto=talle_obj.producto, talle=talle_obj)
            wishlist_obj.save()
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ser = WishListSerializer(wishlist_obj)
        return Response(ser.data, status=status.HTTP_201_CREATED)

class WishListViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = WishListSerializer
    queryset = WishList.objects.all()
    lookup_url_kwarg = "producto_id"
    http_method_names = ['delete']

    def destroy(self, request, *args, **kwargs):
        try:
            producto_id = kwargs.get('producto_id')
        except:
            return Response({'error': 'Falta el producto_id'}, status=status.HTTP_400_BAD_REQUEST)

        username_auth = request.user.username

        qs_wishlist_obj = WishList.objects.filter(usuario__username=username_auth, producto__id=producto_id)

        if not qs_wishlist_obj.exists():
            return Response({'error': 'Producto inexistente en WishList'}, status=status.HTTP_404_NOT_FOUND)

        list_attrs = []
        for instance in qs_wishlist_obj:
            attrs = {'username': instance.usuario.username , 'articulo_id': instance.talle.id, 'producto_id': instance.producto.id, 'nombre_producto': instance.producto.nombre_producto, 'talle': instance.talle.talle}
            list_attrs.append(attrs)

        qs_wishlist_obj.delete()

        return Response(list_attrs[0], status=status.HTTP_204_NO_CONTENT)


class GetWishListViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = WishList.objects.all()
    serializer_class = GetWishListSerializer
    http_method_names = ['get']

    def get_queryset(self):
        """
        Esta vista retorna el WishList del usuario que está logueado
        """
        user = self.request.user
        queryset = self.queryset.filter(usuario=user)

        return queryset

class GetPerfilMarcaViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Marca.objects.all()
    serializer_class = GetPerfilMarcaSerializer

    def get_queryset(self):
        """
        Esta vista retorna el Usuario Marca segun parámetro del Request
        """

        try:
            marca_id = self.kwargs['marca_id']
        except:
            raise exceptions.NotFound(detail="Marca Id no informada por parámetro")

        try:
            marca_obj = Marca.objects.get(pk=marca_id)
        except:
            raise exceptions.NotFound(detail="Marca inválida o inexistente")

        queryset = self.queryset.filter(pk=marca_id)

        return queryset

class MarcaLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Marca.objects.all()
    serializer_class = MarcaLogSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        else:
            queryset = self.queryset

        return queryset

class MarcaCategoriaLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Marca.objects.all()
    serializer_class = MarcaCategoriaLogSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        else:
            queryset = self.queryset

        return queryset

class LocalesLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Marca.objects.all()
    serializer_class = LocalesLogSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        else:
            queryset = self.queryset

        return queryset

class NovedadesLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Marca.objects.all()
    serializer_class = NovedadesLogSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            queryset = self.queryset.filter(pk=marca_id)
        else:
            queryset = self.queryset

        return queryset

class OfertasMarcaLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Producto.objects.all()
    serializer_class = OfertasSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            fecha_hoy = datetime.date.today()
            queryset = self.queryset.filter(marca__id=marca_id, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy).order_by('-date_created')
        else:
            raise exceptions.NotFound(detail="Marca_id inválida o inexistente")

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(queryset, request)

        return result_page

class OfertasMarcaCategoriaLogViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Producto.objects.all()
    serializer_class = OfertasSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        marca_id = self.kwargs['marca_id']
        if marca_id is not None:
            fecha_hoy = datetime.date.today()
            queryset = self.queryset.filter(marca__id=marca_id, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy)
        else:
            raise exceptions.NotFound(detail="Marca_id inválida o inexistente")

        categoria_id = self.kwargs['categoria_id']
        if categoria_id is not None:
            try:
                categoria_obj = Categoria.objects.get(pk=categoria_id)
            except:
                raise exceptions.NotFound(detail="Categoria_id inválida o inexistente")
            else:
                lista_categorias = categoria_obj.get_subcategorias()
        else:
            raise exceptions.NotFound(detail="Categoria_id inválida o inexistente")

        queryset = queryset.filter(categoria__in=lista_categorias).order_by('-date_created')

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(queryset, request)

        return result_page

class DescuentosViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Producto.objects.all()
    serializer_class = OfertasSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        user = self.request.user
        try:
            user_id = user.id
        except:
            qs_marcas_seguidas = MarcaSeguida.objects.none()
        else:
            qs_marcas_seguidas = MarcaSeguida.objects.filter(usuario_id=user_id).values('marca')
        queryset1 = Marca.objects.filter(pk__in=qs_marcas_seguidas)
        queryset2 = Marca.objects.exclude(pk__in=qs_marcas_seguidas)

        # Se buscan productos en oferta
        fecha_hoy = datetime.date.today()
        qs_productos1 = self.queryset.filter(marca__in=queryset1, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy).order_by('-date_created')
        qs_productos2 = self.queryset.filter(marca__in=queryset2, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy).order_by('-date_created')

        qs_all_ofertas = qs_productos1.union(qs_productos2, all=True)

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(qs_all_ofertas, request)

        return result_page

class DescuentosCategoriaViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Producto.objects.all()
    serializer_class = OfertasSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        user = self.request.user

        categoria_id = self.kwargs['categoria_id']
        if categoria_id is not None:
            try:
                categoria_obj = Categoria.objects.get(pk=categoria_id)
            except:
                raise exceptions.NotFound(detail="Categoria_id inválida o inexistente")
            else:
                lista_categorias = categoria_obj.get_subcategorias()
        else:
            raise exceptions.NotFound(detail="Categoria_id inválida o inexistente")

        try:
            user_id = user.id
        except:
            qs_marcas_seguidas = MarcaSeguida.objects.none()
        else:
            qs_marcas_seguidas = MarcaSeguida.objects.filter(usuario_id=user_id).values('marca')
        queryset1 = Marca.objects.filter(pk__in=qs_marcas_seguidas)
        queryset2 = Marca.objects.exclude(pk__in=qs_marcas_seguidas)

        # Se buscan productos en oferta
        fecha_hoy = datetime.date.today()
        qs_productos1 = self.queryset.filter(marca__in=queryset1, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy,
                              categoria__in=lista_categorias).order_by('-date_created')
        qs_productos2 = self.queryset.filter(marca__in=queryset2, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy,
                              categoria__in=lista_categorias).order_by('-date_created')

        qs_all_ofertas = qs_productos1.union(qs_productos2, all=True)

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(qs_all_ofertas, request)

        return result_page

class DetalleProductoViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Producto.objects.all()
    serializer_class = DetalleProductoSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        producto_id = self.kwargs['producto_id']
        #print ('marca_id: ', marca_id)
        if producto_id is not None:
            queryset = self.queryset.filter(pk=producto_id)
        user = self.request.user
        try:
            user_comprador_obj = UserComprador.objects.get(username=user.username)
            producto_obj = Producto.objects.get(pk=producto_id)
        except:
            pass
            #raise exceptions.NotFound(detail="Producto o usuario no encontrado")
        else:
            # Se registra la vista del Producto en VistaUsuarioProducto
            vista_producto = VistaUserProducto.objects.create(usuario=user_comprador_obj, producto=producto_obj)

        return queryset

class DetallePostViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = Post.objects.all()
    serializer_class = VidrieraSerializer
    http_method_names = ['get', 'head']

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        if post_id is not None:
            queryset = self.queryset.filter(pk=post_id)

        try:
            post_obj = Post.objects.get(pk=post_id)
        except:
            raise exceptions.NotFound(detail="Post_Id inválido o inexistente")

        return queryset

class BuscadorGenericoViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = BuscadorGenericoSerializer


    def get_queryset(self):
        search_string = self.request.query_params.get('search_string', None)

        if not search_string:
            queryset = UserComprador.objects.none()
        else:
            qs_usuarios = UserComprador.objects.filter(
                                    Q(first_name__icontains=search_string) |
                                    Q(last_name__icontains=search_string)  |
                                    Q(username__icontains=search_string))
            # Se excluye de la búsqueda el usuario logueado, en caso que el usuario esté autenticado
            user_auth = self.request.user
            try:
                user_auth_id = user_auth.pk
            except:
                pass
            else:
                qs_usuarios = qs_usuarios.exclude(pk=user_auth_id)

            qs_marcas = Marca.objects.filter(Q(nombre__icontains=search_string) |
                                    Q(descripcion__icontains=search_string) ).distinct()
            qs_productos = Producto.objects.filter(Q(nombre_producto__icontains=search_string) |
                                    Q(descripcion__icontains=search_string) |
                                    Q(tags__slug__icontains=search_string)).distinct()


            list_objects = []
            for usuario in qs_usuarios:
                list_objects.append(usuario)

            for marca in qs_marcas:
                list_objects.append(marca)

            for producto in qs_productos:
                list_objects.append(producto)

            queryset = list_objects

        return queryset

class GetDetallePerfilPropioViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserComprador.objects.all()
    serializer_class = GetDetallePerfilSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        user = self.request.user
        queryset = super(GetDetallePerfilPropioViewSet, self).get_queryset()
        queryset = queryset.filter(pk=user.id)
        return queryset

class GetDetallePerfilOtroViewSet(ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = UserComprador.objects.all()
    serializer_class = GetDetallePerfilSerializer
    http_method_names = ['get',]


    def get_queryset(self):
        """
        Esta vista retorna el Usuario Comprador segun parámetro del Request
        """
        try:
            username_usuario_comprador = self.kwargs['username']
        except:
            raise exceptions.NotFound(detail="Username no informado por parámetro")

        try:
            usuario_comprador = UserComprador.objects.get(username=username_usuario_comprador)
        except:
            raise exceptions.NotFound(detail="El username no corresponde a un Usuario Comprador")

        queryset = self.queryset.filter(username=usuario_comprador.username)

        return queryset

class VidrieraViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    serializer_class = VidrieraSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Se buscan las marcas que sigue el usuario logueado
        user_auth = self.request.user

        if user_auth.username:
            # Usuario Logueado
            qs_marcas_seguidas = MarcaSeguida.objects.filter(usuario__username=user_auth.username).values('marca')
            # Esto porque Django no devuelve objectos con ForeignKey, sino solo las claves
            lista_pks_marcas = []
            for marca in qs_marcas_seguidas:
                lista_pks_marcas.append(marca['marca'])

            qs_marcas = Marca.objects.filter(pk__in=lista_pks_marcas)

            if qs_marcas.count() > 0:
                # Usuario logueado con marcas seguidas
                # Se buscan fotos
                # 1ro se buscan Productos
                #qs_productos = Producto.objects.filter(marca__in=qs_marcas)

                '''
                # 2do se buscan Fotos de Productos
                qs_fotos_productos = FotoProducto.objects.filter(producto__in=qs_productos)
                '''
                # 3ro se buscan Fotos e Imágenes de Colecciones
                #qs_colecciones = Coleccion.objects.filter(marca__in=qs_marcas)

                #qs_fotos_colecciones = FotoColeccion.objects.filter(coleccion__in=qs_colecciones)
                # 4to se buscan Fotos e Imágenes de Posteos
                qs_posteos = Post.objects.filter(marca__in=qs_marcas)
                #qs_imagenes_posteos = ImagenPost.objects.filter(post__in=qs_posteos)


            else:
                # Usuario logueado sin marcas seguidas
                # Se obtienen productos de acuerdo al perfil de usuario
                #user_comprador = UserComprador.objects.get(username=user_auth.username)
                #genero = user_comprador.genero
                #if genero == 'M':
                #    filter_productos = ['HOMBRE', 'AMBOS SEXOS']
                #else:
                #    filter_productos = ['MUJER', 'AMBOS SEXOS']
                #qs_productos = Producto.objects.filter(segmento_sexo__in=filter_productos).order_by('-date_created')
                '''
                # 2do se buscan Fotos de Productos
                qs_fotos_productos = FotoProducto.objects.filter(producto__in=qs_productos)
                '''
                #qs_fotos_colecciones = FotoColeccion.objects.none()
                # Se buscan los ultimos posts
                qs_posteos = Post.objects.all()

        else:
            # Usuario sin loguear - Se buscan los ultimos posts
                #qs_productos = Producto.objects.all()
                #qs_fotos_productos = FotoProducto.objects.all()
                #qs_fotos_colecciones = FotoColeccion.objects.all()
                qs_posteos = Post.objects.all()

        '''
        # Se arman listas para cada queryset
        #lista_productos =  list(qs_productos)
        #lista_fotos_productos = list(qs_fotos_productos)
        #lista_fotos_colecciones = list(qs_fotos_colecciones)
        lista_imagenes_posteos = list(qs_imagenes_posteos)

        # Se juntan las listas y se ordenan por date_created descendente
        from itertools import chain
        from operator import attrgetter
        #result_list = sorted(chain(lista_productos, lista_fotos_colecciones, lista_imagenes_posteos),
        #                key=attrgetter('date_created'), reverse=True)

        result_list = sorted(chain(lista_imagenes_posteos),
                        key=attrgetter('date_created'), reverse=True)
        '''

        # Se ordena el queryset por: 1) Fecha de creación del Post descendente
        qs_posteos_sorted = qs_posteos.order_by('-date_created')

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(qs_posteos_sorted, request)

        return result_page

class ImagenesBuscadorViewSet(viewsets.ViewSetMixin, generics.ListAPIView):
    serializer_class = ImagenesBuscadorSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        # Se buscan los productos con más favoritos y las imágenes de los Posts con más likes
        # luego el resto aunque pertenezcan a marcas no seguidas
        from django.db.models import Count
        qs_count_productos_favoritos = WishList.objects.all().values('producto').annotate(total=Count('producto')).order_by('-total')
        list_productos_favoritos = []
        for item in qs_count_productos_favoritos:
            list_productos_favoritos.append(item['producto'])

        qs_count_likes_posts = LikePost.objects.all().values('post').annotate(total=Count('post')).order_by('-total')
        list_likes_posts = []
        for item in qs_count_likes_posts:
            list_likes_posts.append(item['post'])

        # Se arman 6 querysets y luego se los une
        qs_productos_fav = Producto.objects.filter(pk__in=list_productos_favoritos)
        qs_productos_no_fav = Producto.objects.exclude(pk__in=list_productos_favoritos).order_by('-date_created')

        qs_imagenes_posts_likes = ImagenPost.objects.filter(post__in=list_likes_posts)
        qs_imagenes_posts_no_like = ImagenPost.objects.exclude(post__in=list_likes_posts).order_by('-date_created')

        #qs_videos_posts_likes = VideoLinkPost.objects.filter(post__in=list_likes_posts)
        #qs_videos_posts_no_likes = VideoLinkPost.objects.exclude(post__in=list_likes_posts).order_by('-date_created')

        # Se juntan las listas
        from itertools import chain
        result_list = list(chain(list(qs_productos_fav), list(qs_imagenes_posts_likes),
                      list(qs_productos_no_fav), list(qs_imagenes_posts_no_like)))

        paginator = LimitOffsetPagination()
        request = self.request
        result_page = paginator.paginate_queryset(result_list, request)

        return result_page

'''
class LikeFotoColeccionViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = LikeFotoColeccion.objects.all()
    serializer_class = LikeFotoColeccionSerializer
    lookup_url_kwarg = "foto_coleccion_id"

    def get_queryset(self):
        """
        Esta vista retorna los likes de las fotos de colecciones del usuario que está logueado
        """
        foto_coleccion_id = self.kwargs.get(self.lookup_url_kwarg)
        foto_coleccion_obj = FotoColeccion.objects.get(pk=foto_coleccion_id)
        user = self.request.user
        return self.queryset.filter(usuario=user, foto_coleccion=foto_coleccion_obj)

    def post(self, request, format=None, *args, **kwargs):
        foto_coleccion_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            foto_coleccion_obj = FotoColeccion.objects.get(pk=foto_coleccion_id)
        except:
            return Response({"error": "La foto de la colección no existe"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        attrs = {'username': user.username , 'foto_coleccion_id': foto_coleccion_obj.id}
        if LikeFotoColeccion.objects.filter(usuario__pk=user.id, foto_coleccion=foto_coleccion_obj).exists():
            return Response({"error": "La foto de la colección ya tiene like"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeFotoColeccionSerializer(data=attrs)
        if serializer.is_valid():
            try:
                #print('el serializer es válido, va a hacer save')
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        foto_coleccion_id = self.kwargs.get(self.lookup_url_kwarg)
        foto_coleccion_obj = FotoColeccion.objects.get(pk=foto_coleccion_id)
        user = request.user
        attrs = {'username': user.username , 'foto_coleccion_id': foto_coleccion_obj.id}
        try:
            instance = LikeFotoColeccion.objects.get(usuario=user, foto_coleccion=foto_coleccion_obj)
            instance.delete()
            return Response(attrs, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
'''

class LikeFotoProductoViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = LikeFotoProducto.objects.all()
    serializer_class = LikeFotoProductoSerializer
    lookup_url_kwarg = "foto_producto_id"

    def get_queryset(self):
        """
        Esta vista retorna los likes de las fotos de productos del usuario que está logueado
        """
        foto_producto_id = self.kwargs.get(self.lookup_url_kwarg)
        foto_producto_obj = FotoProducto.objects.get(pk=foto_producto_id)
        user = self.request.user
        return self.queryset.filter(usuario=user, foto_producto=foto_producto_obj)

    def post(self, request, format=None, *args, **kwargs):
        foto_producto_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            foto_producto_obj = FotoProducto.objects.get(pk=foto_producto_id)
        except:
            return Response({"error": "La foto del producto no existe"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        attrs = {'username': user.username , 'foto_producto_id': foto_producto_obj.id}
        if LikeFotoProducto.objects.filter(usuario__pk=user.id, foto_producto=foto_producto_obj).exists():
            return Response({"error": "La foto del producto ya tiene like"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeFotoProductoSerializer(data=attrs)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        foto_producto_id = self.kwargs.get(self.lookup_url_kwarg)
        foto_producto_obj = FotoProducto.objects.get(pk=foto_producto_id)
        user = request.user
        attrs = {'username': user.username , 'foto_producto_id': foto_producto_obj.id}
        try:
            instance = LikeFotoProducto.objects.get(usuario=user, foto_producto=foto_producto_obj)
            instance.delete()
            return Response(attrs, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class LikePostViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = LikePost.objects.all()
    serializer_class = LikePostSerializer
    lookup_url_kwarg = "post_id"

    def get_queryset(self):
        """
        Esta vista retorna los likes de posts del usuario que está logueado
        """
        post_id = self.kwargs.get(self.lookup_url_kwarg)
        post_obj = Post.objects.get(pk=post_id)
        user = self.request.user
        return self.queryset.filter(usuario=user, post=post_obj)

    def post(self, request, format=None, *args, **kwargs):
        post_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            post_obj = Post.objects.get(pk=post_id)
        except:
            return Response({"error": "El post no existe"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        attrs = {'username': user.username , 'post_id': post_obj.id}
        if LikePost.objects.filter(usuario__pk=user.id, post=post_obj).exists():
            return Response({"error": "El post ya tiene like"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikePostSerializer(data=attrs)
        if serializer.is_valid():
            try:
                #print('el serializer es válido, va a hacer save')
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        post_id = self.kwargs.get(self.lookup_url_kwarg)
        post_obj = Post.objects.get(pk=post_id)
        user = request.user
        attrs = {'username': user.username , 'post_id': post_obj.id}
        try:
            instance = LikePost.objects.get(usuario=user, post=post_obj)
            instance.delete()
            return Response(attrs, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

'''
class LikeImagenPostViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = LikeImagenPost.objects.all()
    serializer_class = LikeImagenPostSerializer
    lookup_url_kwarg = "imagen_post_id"

    def get_queryset(self):
        """
        Esta vista retorna los likes de las imágenes de posts del usuario que está logueado
        """
        imagen_post_id = self.kwargs.get(self.lookup_url_kwarg)
        imagen_post_obj = ImagenPost.objects.get(pk=imagen_post_id)
        user = self.request.user
        return self.queryset.filter(usuario=user, imagen_post=imagen_post_obj)

    def post(self, request, format=None, *args, **kwargs):
        imagen_post_id = self.kwargs.get(self.lookup_url_kwarg)
        try:
            imagen_post_obj = ImagenPost.objects.get(pk=imagen_post_id)
        except:
            return Response({"error": "La imagen del post no existe"}, status=status.HTTP_404_NOT_FOUND)
        user = request.user

        attrs = {'username': user.username , 'imagen_post_id': imagen_post_obj.id}
        if LikeImagenPost.objects.filter(usuario__pk=user.id, imagen_post=imagen_post_obj).exists():
            return Response({"error": "La imagen del post ya tiene like"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LikeImagenPostSerializer(data=attrs)
        if serializer.is_valid():
            try:
                #print('el serializer es válido, va a hacer save')
                serializer.save()
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        imagen_post_id = self.kwargs.get(self.lookup_url_kwarg)
        imagen_post_obj = ImagenPost.objects.get(pk=imagen_post_id)
        user = request.user
        attrs = {'username': user.username , 'imagen_post_id': imagen_post_obj.id}
        try:
            instance = LikeImagenPost.objects.get(usuario=user, imagen_post=imagen_post_obj)
            instance.delete()
            return Response(attrs, status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
'''

class AvisoFaltaStockViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = AvisoFaltaStock.objects.all()
    serializer_class = AvisoFaltaStockSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        """
        Esta vista retorna los avisos de falta de stock del usuario que está logueado
        """
        user = self.request.user
        queryset = self.queryset.filter(usuario=user)

        try:
            talle_id = self.kwargs['talle_id']
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            talle_obj = TalleProducto.objects.get(pk=talle_id)
        except:
            return Response({"error": "Artículo de ese talle_id inexistente"}, status=status.HTTP_404_NOT_FOUND)

        self.username = user.username

        queryset = queryset.filter(articulo=talle_obj)

        return queryset


    def create(self, request, format=None, *args, **kwargs):
        user = request.user

        talle_id = kwargs.get('talle_id')

        try:
            talle_obj = TalleProducto.objects.get(pk=talle_id)
        except:
            return Response({"error": "Artículo de ese talle_id inexistente"}, status=status.HTTP_404_NOT_FOUND)

        user_obj = UserComprador.objects.get(username=user.username)
        attrs = {'username': user.username , 'id_producto': talle_obj.producto.pk, 'nombre_producto': talle_obj.producto.nombre_producto, 'talle_id': talle_obj.id, 'talle_desc': talle_obj.talle}

        if AvisoFaltaStock.objects.filter(usuario__pk=user.id, articulo=talle_obj).exists():
            return Response({"error": "El artículo ya tiene aviso de stock"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AvisoFaltaStockSerializer(data=attrs)
        if serializer.is_valid():
            try:
                nuevo_aviso_obj = serializer.save()
                attrs['id'] = nuevo_aviso_obj.pk
                return Response(attrs, status=status.HTTP_201_CREATED)
            except:
               # ('el serializer no es válido')
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificacionViewSet(ModelViewSet):
    authentication_classes = (OAuth2Authentication, BearerTokenAuthentication)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(
            usuario=user, leida=False, archivar=False)
        return queryset

    @detail_route
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.leida = True
        notificacion.leida_fecha = timezone.now()
        notificacion.save()
        return Response(status=status.HTTP_200_OK)

    @detail_route
    def marcar_archivada(self, request, pk=None):
        notificacion = self.get_object()
        notificacion.archivar = True
        notificacion.archivar_fecha = timezone.now()
        notificacion.save()
        return Response(status=status.HTTP_200_OK)


class ProcesoBatchViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProcesoBatch.objects.all()
    serializer_class = ProcesoBatchSerializer
    http_method_names = ['get', 'post']

    def get_queryset(self):
        marca_id = self.kwargs.get('marca_id')

        if marca_id is not None:
            queryset = self.queryset.filter(marca_id=marca_id)

        else:
            queryset = EmptyQuerySet

        return queryset


class ProcesoBatchErrorViewSet(ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ProcesoBatchError.objects.all()
    serializer_class = ProcesoBatchErrorSerializer
    http_method_names = ['get']

    def get_queryset(self):
        marca_id = self.kwargs.get('marca_id')

        if marca_id is not None:
            queryset = self.queryset.filter(proceso_batch__marca_id=marca_id)

        else:
            queryset = EmptyQuerySet

        return queryset


class GetProductoActualizacionPrecioDescuentoCSV(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Producto.objects.all()

    def get(self, request, format=None):
        user_request = self.request.user
        # Esto lo tengo que hacer porque del request.user no se obtiene directamente el UserMarca
        try:
            user_marca = UserMarca.objects.get(username=user_request.username)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            marca_id = user_marca.marca.pk

        campos = [
            'id',
            'nombre_producto',
            'precio',
            'porc_descuento',
            'fecha_descuento_desde',
            'fecha_descuento_hasta',
        ]
        marca = user_marca.marca
        productos = marca.producto_marca.all().order_by('pk')

        fd = io.StringIO()
        csv_writer = csv.DictWriter(fd, fieldnames=campos)
        csv_writer.writeheader()

        for producto in productos:
            csv_writer.writerow({f: getattr(producto, f) for f in campos})

        response = HttpResponse(fd.getvalue(), content_type='application/csv')

        fecha = timezone.now()
        csv_name = '{}-{}_{}-actualizacion-precio-descuento'.format(
            fecha.year, fecha.month, marca)

        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            csv_name)

        return response


class GetProductoActualizacionStockCSV(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = TalleProducto.objects.all()

    def get(self, request, format=None):

        user_request = self.request.user
        # Esto lo tengo que hacer porque del request.user no se obtiene directamente el UserMarca
        try:
            user_marca = UserMarca.objects.get(username=user_request.username)
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            marca_id = user_marca.marca.pk

        campos = [
            'id',
            'nombre_producto',
            'talle',
            'shop_sku',
            'stock',
        ]
        marca = user_marca.marca
        talle_productos = TalleProducto.objects.filter(
            producto__marca=marca).order_by('pk')

        fd = io.StringIO()
        csv_writer = csv.DictWriter(fd, fieldnames=campos)
        csv_writer.writeheader()

        for talle_producto in talle_productos:
            row = {
                'id': talle_producto.id,
                'nombre_producto': talle_producto.producto.nombre_producto,
                'talle': talle_producto.talle,
                'shop_sku': talle_producto.shop_sku,
                'stock': talle_producto.stock,
            }
            csv_writer.writerow(row)

        response = HttpResponse(fd.getvalue(), content_type='application/csv')

        fecha = timezone.now()
        csv_name = '{}-{}_{}-actualizacion-stock.csv'.format(
            fecha.year, fecha.month, marca)

        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            csv_name)

        return response


class UploadImageViewSet(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)