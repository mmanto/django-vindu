# -*- encoding: utf-8 -*-
from rest_framework import serializers, exceptions

from .models import *
from auth_api.models import UserComprador, UserMarca, UsuarioSeguido
from django.db.models import Count
from auth_api.serializers import UserCompradorSerializer
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
import datetime
from embed_video.backends import detect_backend
from carrito.models import Pedido


def get_foto_or_null(foto_obj, context):
    try:
        url = foto_obj.url
    except:
        return ''
    else:
        request = context.get('request')
        photo_url = foto_obj.url
        return request.build_absolute_uri(photo_url)


class CategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Categoria
        fields = '__all__'

class MarcaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marca
        fields = ('id', 'nombre')

class DepositoSerializer(serializers.ModelSerializer):
    marca  = MarcaSerializer(read_only=True, many=False, source='deposito_marca')
    cod_postal = serializers.SerializerMethodField()

    class Meta:
        model = Deposito
        fields = ('nombre_deposito', 'marca', 'ind_deposito_default', 'contacto_deposito',
                  'telefono_contacto', 'calle', 'numero', 'piso', 'departamento', 'provincia',
                  'localidad', 'cod_postal')

    def get_cod_postal(self, obj):
        return obj.cod_postal.cod_postal


class FotoLocalSerializer(serializers.ModelSerializer):

    class Meta:
        model = FotoLocal
        fields = ('foto_local')


class LocalSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_local')
    foto   = serializers.SerializerMethodField('get_first_foto')

    def get_first_foto(self, obj):
        first_foto = FotoLocal.objects.filter(pk=obj.id)[0]
        #print ('first_foto:', first_foto)
        #serializer = FotoLocalSerializer(instance=first_foto, many=False)
        #return first_foto.foto_local.url
        return self.context['request'].build_absolute_uri(first_foto.foto_local.url)

    class Meta:
        model = Local
        fields = ('nombre', 'direccion', 'ciudad', 'telefono', 'latitud', 'longitud', 'foto')

class FotoNovedadSerializer(serializers.ModelSerializer):

    class Meta:
        model = FotoNovedad
        fields = ('id', 'foto_novedad',)

'''
class FotoColeccionSerializer(serializers.ModelSerializer):

    class Meta:
        model = FotoColeccion
        fields = ('id', 'foto_coleccion',)
'''

class NovedadSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source='titulo_novedad')
    fotos  = FotoNovedadSerializer(read_only=True, many=True, source='foto_rel_novedad')

    class Meta:
        model = Novedad
        fields = ('titulo', 'descripcion', 'fotos')

class FotoProductoSerializer(serializers.ModelSerializer):
    foto_producto   = serializers.SerializerMethodField()

    class Meta:
        model = FotoProducto
        fields = ('id', 'foto_producto',)

    def get_foto_producto(self, obj):
        if obj.foto_producto_optim:
            return get_foto_or_null(obj.foto_producto_optim, self.context)
        else:
            return get_foto_or_null(obj.foto_producto, self.context)

class TomaFoto360Serializer(serializers.ModelSerializer):

    class Meta:
        model = TomaFoto360
        fields = ('id', 'foto360_imagen',)

    def get_foto360_imagen(self, obj):
        return get_foto_or_null(obj.foto360_imagen, self.context)


class Foto360ProductoSerializer(serializers.ModelSerializer):
    array_imagenes = serializers.SerializerMethodField()

    class Meta:
        model = Foto360Producto
        fields = ('id', 'descripcion', 'array_imagenes')

    def get_array_imagenes(self, obj):
        qs_tomas_360 = TomaFoto360.objects.filter(foto360=obj).order_by('pk')
        request = self.context.get('request')
        ser = TomaFoto360Serializer(qs_tomas_360, many=True, context={'request':request})
        return ser.data


class TalleProductoSerializer(serializers.ModelSerializer):

    class Meta:
        model = TalleProducto
        fields = ('id', 'talle', 'shop_sku', 'stock')


class ProductoSummarySerializer(serializers.ModelSerializer):
    oferta = serializers.SerializerMethodField('get_ind_oferta')
    foto   = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    precio_oferta = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = ('id', 'nombre_producto', 'cod_producto', 'color', 'oferta', 'precio', 'precio_oferta', 'categoria', 'foto')

    def get_ind_oferta(self, obj):
        return obj.ind_oferta()

    def get_foto(self, obj):
        if obj.foto_principal_thumb:
            return get_foto_or_null(obj.foto_principal_thumb, self.context)
        else:
            return get_foto_or_null(obj.foto_principal, self.context)

    def get_precio(self, obj):
        return obj.precio

    def get_precio_oferta(self, obj):
        return obj.get_precio_actual()


class ProductoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_producto')
    oferta = serializers.SerializerMethodField('get_ind_oferta')
    foto   = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    precio_oferta = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = ('id', 'nombre', 'nombre_marca', 'cod_producto', 'color', 'oferta', 'precio', 'precio_oferta', 'categoria', 'foto')

    def get_ind_oferta(self, obj):
        return obj.ind_oferta()

    def get_foto(self, obj):
        if obj.foto_principal_thumb:
            return get_foto_or_null(obj.foto_principal_thumb, self.context)
        else:
            return get_foto_or_null(obj.foto_principal, self.context)

    def get_nombre_marca(self, obj):
        return obj.marca.nombre

    def get_precio_oferta(self, obj):
        return obj.get_precio_actual()


class ColorSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super(ColorSerializer, self).to_representation(instance)
        ret = ret['otro_color']
        return ret

    class Meta:
        model = ColorProducto
        fields = ('otro_color', )
        depth = 1

class CombinacionSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super(CombinacionSerializer, self).to_representation(instance)
        ret = ret['combina_con']
        return ret

    class Meta:
        model = Combinacion
        fields = ('combina_con',)
        depth = 1


class ProductosAdminByMarcaCategoriaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Producto
        fields = ('id', 'nombre_producto', 'foto_principal')

class MarcaAllSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='nombre')
    marca_logo = serializers.ImageField(source='logo')
    locales    = LocalSerializer(read_only=True, many=True, source='local_marca')
    novedades  = NovedadSerializer(read_only=True, many=True, source='novedad_marca')
    productos  = ProductoSerializer(read_only=True, many=True, source='producto_marca')

    class Meta:
        model = Marca
        fields = ('marca_nombre', 'marca_logo', 'locales', 'novedades', 'productos')


class FiltrosCategoriasMarcaSerializer(serializers.ModelSerializer):
    categorias = serializers.SerializerMethodField('get_count_productos_by_categoria')

    def get_count_productos_by_categoria(self, obj):
        list_count_productos_categoria = []
        qs_categorias_padre = Categoria.objects.filter(categoria_padre__isnull=True)
        for categoria_padre in qs_categorias_padre:
            # Se incluyen las categorias de la rama del padre
            categoria_search = categoria_padre.get_subcategorias()
            count_products = Producto.objects.filter(marca=obj, categoria__in=categoria_search).count()
            imagen_categoria = get_foto_or_null(categoria_padre.imagen, self.context)
            dict = {'categoria_id': categoria_padre.id, 'categoria_nombre': categoria_padre.nombre, 'imagen_categoria': imagen_categoria, 'cantidad': count_products}
            list_count_productos_categoria.append(dict)
        return list_count_productos_categoria

    class Meta:
        model = Marca
        fields = ('categorias',)


class MarcaSeguidaSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_marca_seguida')
    marca_id = serializers.IntegerField(required=False, source='marca_marca_seguida')

    class Meta:
        model = MarcaSeguida
        fields = ('username', 'marca_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_marca_id(self, marca_id):
        if not Marca.objects.filter(pk=marca_id).exists():
            raise serializers.ValidationError("La marca no existe")
        return marca_id

    def create(self, validated_data):
        marca_id = validated_data['marca_marca_seguida']
        username_comprador = validated_data['usuario_marca_seguida']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        marca_obj = Marca.objects.get(pk=marca_id)
        try:
            marca_seguida = MarcaSeguida.objects.create(usuario=user_comprador, marca=marca_obj)
        except:
            raise serializers.ValidationError("No se pudo crear la marca seguida")

        return marca_seguida

'''
class ProductoFavoritoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='producto_producto_favorito')
    producto_id = serializers.IntegerField(required=False, source='producto_producto_favorito')

    class Meta:
        model = ProductoFavorito
        fields = ('username', 'producto_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_producto(self, producto_id):
        if not Producto.objects.get(pk=producto_id).exists():
            raise serializers.ValidationError("El producto no existe")
        return producto_id

    def create(self, validated_data):
        producto_id = self.validated_data['producto_producto_favorito']
        username_comprador = self.initial_data['username']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        producto_obj = Producto.objects.get(pk=producto_id)
        try:
            producto_favorito = ProductoFavorito.objects.create(usuario=user_comprador, producto=producto_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el producto como favorito")

        return producto_favorito
'''

class WishListSerializer(serializers.ModelSerializer):
    articulo_id = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    producto_id = serializers.SerializerMethodField()
    nombre_producto = serializers.SerializerMethodField()
    talle = serializers.SerializerMethodField()

    def get_articulo_id(self, obj):
        return obj.talle.id

    def get_username(self, obj):
        return obj.usuario.username

    def get_producto_id(self, obj):
        return obj.producto.id

    def get_nombre_producto(self, obj):
        return obj.producto.nombre_producto

    def get_talle(self, obj):
        return obj.talle.talle

    class Meta:
        model = WishList
        fields = ('articulo_id', 'username', 'producto_id', 'nombre_producto', 'talle')

 

class GetWishListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    producto = ProductoSerializer()
    talle = serializers.SerializerMethodField()
    articulo_id = serializers.SerializerMethodField()

    def get_username(self, obj):
        return obj.usuario.username

    def get_talle(self, obj):
        return obj.talle.talle

    def get_articulo_id(self, obj):
        return obj.talle.pk

    class Meta:
        model = WishList
        fields = ('id', 'username', 'producto', 'articulo_id', 'talle')
        

class ImagenPerfilMarcaSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    id_post = serializers.SerializerMethodField()
    imagen  = serializers.SerializerMethodField()
    tipo_imagen = serializers.SerializerMethodField()
    nombre  = serializers.SerializerMethodField()
    tipo_objeto = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_id_post(self, obj):
        clase = obj.__class__.__name__
        if clase == 'ImagenPost' or clase == 'VideoLinkPost':
            return obj.post.id
        else:
            return None

    def get_imagen(self, obj):
        clase = obj.__class__.__name__

        #if clase == 'Producto':
        #    if obj.foto_principal_thumb:
        #        return get_foto_or_null(obj.foto_principal_thumb, self.context)
        #    else:
        #        return get_foto_or_null(obj.foto_principal, self.context)

        if clase == 'ImagenPost':
            if obj.imagen_post_thumb:
                return get_foto_or_null(obj.imagen_post_thumb, self.context)
            else:
                return get_foto_or_null(obj.imagen_post, self.context) 
        elif clase == 'VideoLinkPost':
            link_video = detect_backend(obj.video_link)
            return link_video.url              
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_imagen(self, obj):
        import mimetypes

        clase = obj.__class__.__name__

        #if clase == 'Producto':
        #    return mimetypes.guess_type(get_foto_or_null(obj.foto_principal, self.context))[0]

        if clase == 'ImagenPost':
            return mimetypes.guess_type(get_foto_or_null(obj.imagen_post, self.context))[0]
        elif clase == 'VideoLinkPost':
            return 'video/youtube'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_nombre(self, obj):
        clase = obj.__class__.__name__

        #if clase == 'Producto':
        #    return obj.nombre_producto

        if clase == 'ImagenPost' or clase == 'VideoLinkPost':
            return obj.post.nombre_post
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_objeto(self, obj):
        clase = obj.__class__.__name__
        #if clase == 'Producto':
        #    return 'Producto'

        if clase == 'ImagenPost':
            return 'ImagenPost'
        elif clase == 'VideoLinkPost':
            return 'VideoLinkPost'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")


class GetPerfilMarcaSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.CharField(source='nombre')
    logo_banner = serializers.ImageField(source='logo')
    user_marca = serializers.SerializerMethodField()
    descripcion = serializers.CharField()
    sitio_web = serializers.CharField()
    marca_seguida = serializers.SerializerMethodField()
    cant_seguidores = serializers.SerializerMethodField()
    imagenes  = serializers.SerializerMethodField()

    def get_user_marca(self, obj):
        qs_users_marca = UserMarca.objects.filter(marca=obj).order_by('pk')
        if qs_users_marca.count() > 0:
            user_marca_username = qs_users_marca[0].username
        else:
            user_marca_username = None
        return user_marca_username

    def get_marca_seguida(self, obj):
        flag_marca_seguida = obj.get_marca_seguida(self)
        return flag_marca_seguida

    def get_cant_seguidores(self, obj):
        return MarcaSeguida.objects.filter(marca=obj).count()

    def get_imagenes(self, obj):
        # Fix: se eliminan los productos, quedan sólo los posteos
        #qs_productos = Producto.objects.filter(marca=obj).order_by('-date_created')
        qs_posteos = Post.objects.filter(marca=obj)
        qs_imagenes_posteos = ImagenPost.objects.filter(post__in=qs_posteos)
        #qs_links_videos = VideoLinkPost.objects.filter(post__in=qs_posteos)

        # Se arman listas para cada queryset
        # lista_productos =  list(qs_productos)
        lista_imagenes_posteos = list(qs_imagenes_posteos)
        #lista_links_videos = list(qs_links_videos)

        # Se juntan las listas y se ordenan por date_created descendente
        from itertools import chain
        from operator import attrgetter
        result_list = sorted(chain(lista_imagenes_posteos),
                        key=attrgetter('date_created'), reverse=True)

        paginator = LimitOffsetPagination()
        request = self.context.get('request')
        result_page = paginator.paginate_queryset(result_list, request)
        serializer = ImagenPerfilMarcaSerializer(result_page, many=True, context={'request':request})
        return serializer.data

    class Meta:
        model = Marca
        fields = ('marca_nombre', 'logo_banner', 'logo_cuadrado', 'user_marca', 'descripcion', 'sitio_web',
                  'marca_seguida', 'cant_seguidores', 'imagenes')


class ProductosByMarcaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_producto')
    oferta = serializers.SerializerMethodField('get_ind_oferta')
    #foto   = serializers.ImageField(source='foto_principal')
    foto = serializers.SerializerMethodField()
    porc_descuento = serializers.SerializerMethodField()
    prod_favorito = serializers.SerializerMethodField()
    talles = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    precio_oferta = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = ('id', 'nombre', 'prod_favorito', 'cod_producto', 'color', 'precio', 'precio_oferta', 'porc_descuento',
                  'oferta', 'categoria', 'foto', 'talles')

    def get_ind_oferta(self, obj):
        return obj.ind_oferta()

    def get_foto(self, obj):
        if obj.foto_principal_thumb:
            return get_foto_or_null(obj.foto_principal_thumb, self.context)
        else:
            return get_foto_or_null(obj.foto_principal, self.context)

    def get_porc_descuento(self, obj):
        fecha_hoy = datetime.date.today()
        fecha_descuento_desde = obj.fecha_descuento_desde
        fecha_descuento_hasta = obj.fecha_descuento_hasta
        if fecha_descuento_desde and fecha_descuento_hasta:
            if obj.fecha_descuento_desde <= fecha_hoy and obj.fecha_descuento_hasta >= fecha_hoy:
                porc_descuento = obj.porc_descuento
            else:
                porc_descuento = 0
        else:
            porc_descuento = 0
        return porc_descuento    

    def get_prod_favorito(self, obj):
        flag_prod_favorito = obj.get_prod_favorito(self)
        return flag_prod_favorito

    def get_talles(self, obj):
        request = self.context.get('request')
        qs_talles = TalleProducto.objects.filter(producto=obj)
        serializer = TalleProductoSerializer(qs_talles, many=True, context={'request':request})
        return serializer.data

    def get_precio(self, obj):
        return obj.precio

    def get_precio_oferta(self, obj):
        return obj.get_precio_actual()

class MarcaLogSerializer(serializers.ModelSerializer):
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    productos = serializers.SerializerMethodField()
    #productos = ProductosLogByMarcaSerializer(many=True, read_only=True, source='producto_marca')

    def get_id_marca(self, obj):
        return obj.id

    def get_nombre_marca(self, obj):
        return obj.nombre

    def get_marca_seguida(self, obj):
        flag_marca_seguida = obj.get_marca_seguida(self)
        return flag_marca_seguida


    def get_productos(self, obj):
        qs_productos = Producto.objects.filter(marca=obj).order_by('-date_created')
        paginator = LimitOffsetPagination()
        request = self.context.get('request')
        result_page = paginator.paginate_queryset(qs_productos, request)
        serializer = ProductosByMarcaSerializer(result_page, many=True, context={'request':request})
        return serializer.data

    class Meta:
        model  = Marca
        fields = ('id_marca', 'nombre_marca', 'marca_seguida', 'productos')

class MarcaCategoriaLogSerializer(serializers.ModelSerializer):
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    productos = serializers.SerializerMethodField()

    def get_id_marca(self, obj):
        return obj.id

    def get_nombre_marca(self, obj):
        return obj.nombre

    def get_marca_seguida(self, obj):
        flag_marca_seguida = obj.get_marca_seguida(self)
        return flag_marca_seguida


    def get_productos(self, obj):
        request = self.context.get('request')
        parser_context = request.parser_context
        kuargs = parser_context['kwargs']
        try:
            categoria_id = kuargs['categoria_id']
            obj_categoria = Categoria.objects.get(pk=categoria_id)
        except:
            raise exceptions.NotFound(detail="Categoría no informada o inexistente")

        lista_categorias = obj_categoria.get_subcategorias()

        qs_productos = Producto.objects.filter(marca=obj, categoria__in=lista_categorias).order_by('-date_created')
        paginator = LimitOffsetPagination()

        result_page = paginator.paginate_queryset(qs_productos, request)
        serializer = ProductosByMarcaSerializer(result_page, many=True, context={'request':request})
        return serializer.data

    class Meta:
        model  = Marca
        fields = ('id_marca', 'nombre_marca', 'marca_seguida', 'productos')

class LocalLogByMarcaSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_local')
    foto   = serializers.SerializerMethodField('get_first_foto')

    def get_first_foto(self, obj):
        qs_fotos_local = FotoLocal.objects.filter(local=obj)
        try:
            first_foto = qs_fotos_local[0]
        except:
            return None
        #print ('first_foto:', first_foto)
        #serializer = FotoLocalSerializer(instance=first_foto, many=False)
        #return first_foto.foto_local.url
        return self.context['request'].build_absolute_uri(first_foto.foto_local.url)

    class Meta:
        model = Local
        fields = ('nombre', 'direccion', 'ciudad', 'telefono', 'latitud', 'longitud', 'foto')


class LocalesLogSerializer(serializers.ModelSerializer):
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    locales = LocalLogByMarcaSerializer(many=True, read_only=True, source='local_marca')

    def get_id_marca(self, obj):
        return obj.id

    def get_nombre_marca(self, obj):
        return obj.nombre

    def get_marca_seguida(self, obj):
        flag_marca_seguida = obj.get_marca_seguida(self)
        return flag_marca_seguida

    class Meta:
        model  = Marca
        fields = ('id_marca', 'nombre_marca', 'marca_seguida', 'locales')


class NovedadLogByMarcaSerializer(serializers.ModelSerializer):
    titulo = serializers.CharField(source='titulo_novedad')
    foto   = serializers.SerializerMethodField('get_first_foto')

    def get_first_foto(self, obj):
        first_foto = FotoNovedad.objects.filter(pk=obj.id)[0]
        return self.context['request'].build_absolute_uri(first_foto.foto_novedad.url)

    class Meta:
        model = Novedad
        fields = ('titulo', 'descripcion', 'foto', 'date_created')

class NovedadesLogSerializer(serializers.ModelSerializer):
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    novedades = serializers.SerializerMethodField()

    def get_id_marca(self, obj):
        return obj.id

    def get_nombre_marca(self, obj):
        return obj.nombre

    def get_marca_seguida(self, obj):
        flag_marca_seguida = obj.get_marca_seguida(self)
        return flag_marca_seguida

    def get_novedades(self, obj):
        qs_novedades = Novedad.objects.filter(marca=obj).order_by('-date_created')
        serializer_nov = NovedadLogByMarcaSerializer(qs_novedades, many=True, context={'request': self.context.get('request')})
        return serializer_nov.data

    class Meta:
        model  = Marca
        fields = ('id_marca', 'nombre_marca', 'marca_seguida', 'novedades')

class OfertasSerializer(serializers.ModelSerializer):
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    producto_oferta = serializers.SerializerMethodField()

    def get_id_marca(self, obj):
        return obj.marca.id

    def get_nombre_marca(self, obj):
        return obj.marca.nombre

    def get_marca_seguida(self, obj):
        obj_marca = obj.marca
        flag_marca_seguida = obj_marca.get_marca_seguida(self)
        return flag_marca_seguida

    def get_producto_oferta(self, obj):
        #qs_ofertas = Producto.objects.filter(marca_id=obj.id, ind_oferta=True)
        #qs_ofertas = obj.get_productos_oferta_por_marca()
        ofertas_serializer = ProductosByMarcaSerializer(obj, context={'request': self.context.get('request')})
        return ofertas_serializer.data

    class Meta:
        model  = Producto
        fields = ('id_marca', 'nombre_marca', 'marca_seguida', 'producto_oferta')

class DetalleProductoSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source='nombre_producto')
    prod_favorito = serializers.SerializerMethodField()
    oferta = serializers.SerializerMethodField('get_ind_oferta')
    foto   = serializers.SerializerMethodField()
    fotos  = FotoProductoSerializer(read_only=True, many=True, source='foto_rel_producto')
    fotos_360  = Foto360ProductoSerializer(read_only=True, many=True, source='foto360_rel_producto')
    otros_colores = serializers.SerializerMethodField()
    talles = serializers.SerializerMethodField()
    combina_con = serializers.SerializerMethodField()
    id_marca = serializers.IntegerField(source='marca.id')
    nombre_marca = serializers.CharField(source='marca.nombre')
    otros_vistos = serializers.SerializerMethodField()
    precio = serializers.SerializerMethodField()
    precio_oferta = serializers.SerializerMethodField()
    tabla_talles = serializers.SerializerMethodField()

    def get_ind_oferta(self, obj):
        return obj.ind_oferta()

    def get_talles(self, obj):
        request = self.context.get('request')
        qs_talles = TalleProducto.objects.filter(producto=obj)
        serializer = TalleProductoSerializer(qs_talles, many=True, context={'request':request})
        return serializer.data

    def get_prod_favorito(self, obj):
        flag_prod_favorito = obj.get_prod_favorito(self)
        return flag_prod_favorito

    def get_foto(self, obj):
        if obj.foto_principal_optim:
            return get_foto_or_null(obj.foto_principal_optim, self.context)
        else:
            return get_foto_or_null(obj.foto_principal, self.context)

    def get_otros_colores(self, obj):
        qs_otros_colores = ColorProducto.objects.filter(producto=obj).select_related('otro_color')
        list_otros_colores = []
        for otro_color in qs_otros_colores:
            list_otros_colores.append(otro_color.otro_color)
        otros_colores_serializer = ProductoSummarySerializer(list_otros_colores, many=True, context={'request': self.context.get('request')})
        return otros_colores_serializer.data

    def get_combina_con(self, obj):
        qs_combina_con = Combinacion.objects.filter(producto=obj).select_related('combina_con')
        list_combina_con = []
        for combinacion in qs_combina_con:
            list_combina_con.append(combinacion.combina_con)
        combinaciones_serializer = ProductoSummarySerializer(list_combina_con, many=True, context={'request': self.context.get('request')})
        return combinaciones_serializer.data

    def get_otros_vistos(self, obj):
        # Usuarios que vieron este producto
        qs_usuarios = VistaUserProducto.objects.filter(producto=obj).values('usuario')

        # Otros productos vistos por usuarios que vieron este producto
        qs_otros_productos = VistaUserProducto.objects.filter(usuario__in=qs_usuarios).exclude(producto=obj)

        # Se deben filtrar productos de la misma marca
        qs_productos_misma_marca = qs_otros_productos.filter(producto__marca=obj.marca)

        qs_productos_pks = qs_productos_misma_marca.values('producto').distinct()

        # Esto porque Django no devuelve objectos con ForeignKey, sino solo las claves
        lista_pks_otros_productos = []
        for otro_prod in qs_productos_pks:
            lista_pks_otros_productos.append(otro_prod['producto'])

        qs_productos = Producto.objects.filter(pk__in=lista_pks_otros_productos)

        otros_prod_serializer =  ProductoSummarySerializer(qs_productos, many=True, context={'request': self.context.get('request')})
        return otros_prod_serializer.data

    def get_precio(self, obj):
        return obj.precio

    def get_precio_oferta(self, obj):
        return obj.get_precio_actual()


    def get_tabla_talles(self, obj):
        # Verifica si el producto tiene tabla de talles propia
        if obj.imagen_talles:
            return get_foto_or_null(obj.imagen_talles, self.context)

        # De lo contrario busca la tabla de talles general
        try:
            tabla_talles_obj = TablaTalles.objects.get(tipo_prenda=obj.tipo_prenda, segmento_sexo=obj.segmento_sexo)     
        except:
            return None

        return get_foto_or_null(tabla_talles_obj.imagen_talles, self.context)


    class Meta:
        model = Producto
        fields = ('id_marca', 'nombre_marca', 'nombre', 'descripcion', 'oferta', 'precio', 'precio_oferta', 'color', 'cod_producto', 'prod_favorito', 'foto', 'fotos', 'fotos_360',
                  'otros_colores', 'talles', 'combina_con', 'otros_vistos', 'tabla_talles')


class BuscadorGenericoSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    imagen  = serializers.SerializerMethodField()
    nombre  = serializers.SerializerMethodField()
    descripcion  = serializers.SerializerMethodField()
    tipo_objeto = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_imagen(self, obj):
        #print ('class: ', obj.__class__.__name__)

        clase = obj.__class__.__name__
        #print ('en get foto, obj: ', obj, ' y clase: , clase')
        if clase == 'UserComprador':
            return get_foto_or_null(obj.foto_avatar, self.context)

        elif clase == 'Producto':
            if obj.foto_principal_thumb:
                return get_foto_or_null(obj.foto_principal_thumb, self.context)
            else:
                return get_foto_or_null(obj.foto_principal, self.context)

        elif clase == 'Marca':
            return get_foto_or_null(obj.logo_cuadrado, self.context)

        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_nombre(self, obj):
        clase = obj.__class__.__name__
        if clase == 'UserComprador':
            return obj.username

        elif clase == 'Producto':
            return obj.nombre_producto

        elif clase == 'Marca':
            return obj.nombre

        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_descripcion(self, obj):
        clase = obj.__class__.__name__
        if clase == 'UserComprador':
            return obj.first_name + ' ' + obj.last_name

        elif clase == 'Producto':
            return obj.descripcion

        elif clase == 'Marca':
            return obj.descripcion

        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_objeto(self, obj):
        clase = obj.__class__.__name__
        if clase == 'UserComprador':
            return 'UserComprador'

        elif clase == 'Producto':
            return 'Producto'

        elif clase == 'Marca':
            return 'Marca'

        else:
            raise exceptions.NotFound(detail="Modelo desconocido")


class GetDetallePerfilSerializer(serializers.ModelSerializer):
    usuario_seguido = serializers.SerializerMethodField()
    #cantidad_seguidores = serializers.SerializerMethodField()
    #lista_seguidores    = serializers.SerializerMethodField()
    cantidad_marcas_seguidas = serializers.SerializerMethodField()
    lista_marcas_seguidas = serializers.SerializerMethodField()
    cantidad_productos_wishlist = serializers.SerializerMethodField()
    lista_wishlist = serializers.SerializerMethodField()
    cantidad_compras = serializers.SerializerMethodField()


    class Meta:
        model = UserComprador
        fields = ('username', 'first_name', 'last_name', 'foto_avatar', 'genero', 'biografia', 'wishlist_publico',
                  'usuario_seguido', 'cantidad_marcas_seguidas', 'lista_marcas_seguidas',
                  'cantidad_productos_wishlist', 'lista_wishlist', 'cantidad_compras' )


    def get_usuario_seguido(self, obj):
        request = self.context.get('request')
        user_auth = request.user

        # Se chequea si el usuario está autenticado
        try:
            user_auth_id = user_auth.id
        except:
            return False

        if UsuarioSeguido.objects.filter(usuario__username=user_auth.username, usuario_seguido=obj).exists():
            return True
        else:
            return False

    '''
    def get_cantidad_seguidores(self, obj):
        request = self.context.get('request')
        user_auth = request.user
        # Se chequea si el usuario está autenticado
        try:
            user_auth_id = user_auth.id
        except:
            return 0

        qs_usuarios_seguidores = UsuarioSeguido.objects.filter(usuario_seguido=obj)
        cantidad = qs_usuarios_seguidores.count()
        return cantidad

    def get_lista_seguidores(self, obj):
        #usuario_logueado = obj
        qs_usuarios_seguidores = UsuarioSeguido.objects.filter(usuario_seguido=obj)

        lista_seguidores = []
        for user in qs_usuarios_seguidores:
            lista_seguidores.append({"username": user.usuario.username })

        return lista_seguidores
    '''

    def get_cantidad_marcas_seguidas(self, obj):
        qs_marcas_seguidas = MarcaSeguida.objects.filter(usuario=obj)
        cantidad = qs_marcas_seguidas.count()
        return cantidad

    def get_lista_marcas_seguidas(self, obj):
        qs_marcas_seguidas = MarcaSeguida.objects.filter(usuario=obj)

        lista_marcas_seguidas = []
        for marca_seguida in qs_marcas_seguidas:
            lista_marcas_seguidas.append({"marca": marca_seguida.marca.nombre})

        return lista_marcas_seguidas

    def get_cantidad_productos_wishlist(self, obj):
        qs_wishlist = WishList.objects.filter(usuario=obj)
        cantidad = qs_wishlist.count()
        return cantidad

    def get_lista_wishlist(self, obj):
        #usuario_logueado = obj

        # Acá se chequea si se debe mostrar o no el WishList:
        # Si el usuario logueado consulta su propio WishList, se lo muestra aunque no sea público
        # Si se consulta el perfil de otro usuario, se chequea si el WishList es público o no
        flag_mostrar_wishlist = True
        request = self.context.get('request')
        user_auth = request.user

        try:
            username_logueado = user_auth.username
        except:
            flag_mostrar_wishlist = False
        else:
            if obj.username != username_logueado:
                if not obj.wishlist_publico:
                    flag_mostrar_wishlist = False

        if flag_mostrar_wishlist:
            qs_wishlist = WishList.objects.filter(usuario=obj)
        else:
            qs_wishlist = WishList.objects.none()

        lista_wishlist = GetWishListSerializer(qs_wishlist, many=True, context={'request': self.context.get('request')})
        '''
        for item in qs_marcas_seguidas:
            producto = item.
            lista_marcas_seguidas.append({"marca": marca_seguida.marca.nombre})
        '''
        #print ('lista_wishlist.data: ', lista_wishlist.data)
        return lista_wishlist.data

    def get_cantidad_compras(self, obj):
        cantidad_compras = Pedido.objects.filter(usuario_comprador=obj).exclude(estado_pedido='I').count()      
        return cantidad_compras

class ImagenesBuscadorSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    id_post = serializers.SerializerMethodField()
    imagen  = serializers.SerializerMethodField()
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    tipo_objeto = serializers.SerializerMethodField()
    tipo_imagen = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_id_post(self, obj):
        clase = obj.__class__.__name__
        if clase == 'ImagenPost':
            return obj.post.id
        else:
            return None

    def get_imagen(self, obj):
        #print ('class: ', obj.__class__.__name__)

        clase = obj.__class__.__name__
        #print ('en get foto, obj: ', obj, ' y clase: , clase')
        if clase == 'Producto':
            if obj.foto_principal_thumb:
                return get_foto_or_null(obj.foto_principal_thumb, self.context)
            else:
                return get_foto_or_null(obj.foto_principal, self.context)

        #elif clase == 'FotoProducto':
        #    return self._get_foto_or_null(obj.foto_producto)

        elif clase == 'ImagenPost':
            if obj.imagen_post_thumb:
                return get_foto_or_null(obj.imagen_post_thumb, self.context)
            else:
                return get_foto_or_null(obj.imagen_post, self.context)  
        elif clase == 'VideoLinkPost':
            link_video = detect_backend(obj.video_link)
            return link_video.url    
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_id_marca(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Producto':
            return obj.marca.id

        #elif clase == 'FotoProducto':
        #    return obj.producto.marca.id
        elif clase == 'ImagenPost' or clase == 'VideoLinkPost':
            return obj.post.marca.id
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_nombre_marca(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Producto':
            return obj.marca.nombre

        #elif clase == 'FotoProducto':
        #    return obj.producto.marca.nombre

        elif clase == 'ImagenPost' or clase == 'VideoLinkPost':
            return obj.post.marca.nombre
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_marca_seguida(self, obj):
        clase = obj.__class__.__name__
        if clase == 'Producto':
            marca = obj.marca

        #elif clase == 'FotoProducto':
        #    marca = obj.producto.marca

        elif clase == 'ImagenPost' or clase == 'VideoLinkPost':
            marca = obj.post.marca
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

        flag_marca_seguida = marca.get_marca_seguida(self)
        return flag_marca_seguida

    def get_tipo_objeto(self, obj):
        clase = obj.__class__.__name__
        if clase == 'Producto':
            return 'Producto'

        #elif clase == 'FotoProducto':
        #    return 'FotoProducto'

        elif clase == 'ImagenPost':
            return 'ImagenPost'
        elif clase == 'VideoLinkPost':
            return 'VideoLinkPost'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_imagen(self, obj):
        import mimetypes

        clase = obj.__class__.__name__

        if clase == 'Producto':
            return mimetypes.guess_type(get_foto_or_null(obj.foto_principal, self.context))[0]

        elif clase == 'ImagenPost':
            return mimetypes.guess_type(get_foto_or_null(obj.imagen_post, self.context))[0]
        elif clase == 'VideoLinkPost':
            return 'video/youtube'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")
    

class ImagenPostSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    imagen  = serializers.SerializerMethodField()
    tipo_objeto = serializers.SerializerMethodField()
    tipo_imagen = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_imagen(self, obj):
        #print ('class: ', obj.__class__.__name__)

        clase = obj.__class__.__name__
        if clase == 'ImagenPost':
            if obj.imagen_post_thumb:
                return get_foto_or_null(obj.imagen_post_thumb, self.context)
            else:
                return get_foto_or_null(obj.imagen_post, self.context) 
        elif clase == 'VideoLinkPost':
            link_video = detect_backend(obj.video_link)
            return link_video.url
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_objeto(self, obj):
        clase = obj.__class__.__name__

        if clase == 'ImagenPost':
            return 'ImagenPost'
        elif clase == 'VideoLinkPost':
            return 'VideoLinkPost'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_tipo_imagen(self, obj):
        import mimetypes

        clase = obj.__class__.__name__

        if clase == 'ImagenPost':
            return mimetypes.guess_type(get_foto_or_null(obj.imagen_post, self.context))[0]
        elif clase == 'VideoLinkPost':
            return 'video/youtube'
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")


class VidrieraSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    id_marca = serializers.SerializerMethodField()
    nombre_marca = serializers.SerializerMethodField()
    marca_seguida = serializers.SerializerMethodField()
    url_logo_marca = serializers.SerializerMethodField()
    nombre_post = serializers.SerializerMethodField()
    descripcion = serializers.SerializerMethodField()
    cant_likes = serializers.SerializerMethodField()
    boolean_like = serializers.SerializerMethodField()
    #imagenes  = ImagenPostSerializer(read_only=True, many=True, source='imagen_post')
    imagenes = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_id_marca(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Post':
            return obj.marca.id
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_nombre_marca(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Post':
            return obj.marca.nombre
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_marca_seguida(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Post':
            marca = obj.marca
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

        flag_marca_seguida = marca.get_marca_seguida(self)
        return flag_marca_seguida

    def get_url_logo_marca(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Post':
            marca = obj.marca
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

        return get_foto_or_null(marca.logo_cuadrado, self.context)

    def get_nombre_post(self, obj):
        clase = obj.__class__.__name__
        if clase == 'Post':
            nombre_post = obj.nombre_post
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

        return nombre_post

    def get_descripcion(self, obj):
        clase = obj.__class__.__name__
        if clase == 'Post':
            descripcion = obj.descripcion
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

        return descripcion


    def get_cant_likes(self, obj):
        clase = obj.__class__.__name__

        if clase == 'Post':
            qs_likes = LikePost.objects.filter(post=obj).count()
            return qs_likes
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_boolean_like(self, obj):
        request = self.context.get('request')
        user_auth = request.user

        username = user_auth.username
        if not username:
            return False

        clase = obj.__class__.__name__
        if clase == 'Post':
            try:
                obj_like = LikePost.objects.get(usuario__username=username, post=obj)
            except:
                return False
            else:
                return True
        else:
            raise exceptions.NotFound(detail="Modelo desconocido")

    def get_imagenes(self, obj):
        qs_fotos_post  = ImagenPost.objects.filter(post=obj)
        qs_videos_post = VideoLinkPost.objects.filter(post=obj)
        # Se arman listas para cada queryset
        lista_fotos_post  = list(qs_fotos_post)
        lista_videos_post = list(qs_videos_post)
        # Se juntan las listas y se ordenan por date_created descendente
        from itertools import chain
        from operator import attrgetter
        result_list = sorted(chain(lista_fotos_post, lista_videos_post),
                        key=attrgetter('date_created'), reverse=True)
        request = self.context.get('request')
        ser_imagenes = ImagenPostSerializer(result_list, read_only=True, many=True, context={'request': request})
        return ser_imagenes.data


'''
class LikeColeccionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_like_coleccion')
    coleccion_id = serializers.IntegerField(required=False, source='coleccion_like_coleccion')

    class Meta:
        model = LikeColeccion
        fields = ('username', 'coleccion_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_coleccion_id(self, coleccion_id):
        if not Coleccion.objects.filter(pk=coleccion_id).exists():
            raise serializers.ValidationError("La colección no existe")
        return coleccion_id

    def create(self, validated_data):
        coleccion_id = self.validated_data['coleccion_like_coleccion']
        username_comprador = self.initial_data['username']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        coleccion_obj = Coleccion.objects.get(pk=coleccion_id)
        try:
            like_coleccion = LikeColeccion.objects.create(usuario=user_comprador, coleccion=coleccion_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el like a la colección")

        return like_coleccion

class LikeFotoColeccionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_like_fotocoleccion')
    foto_coleccion_id = serializers.IntegerField(required=False, source='foto_like_fotocoleccion')

    class Meta:
        model = LikeFotoColeccion
        fields = ('username', 'foto_coleccion_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_foto_coleccion_id(self, foto_coleccion_id):
        if not FotoColeccion.objects.filter(pk=foto_coleccion_id).exists():
            raise serializers.ValidationError("La foto de la colección no existe")
        return foto_coleccion_id

    def create(self, validated_data):
        foto_coleccion_id = self.validated_data['foto_like_fotocoleccion']
        username_comprador = self.initial_data['username']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        foto_coleccion_obj = FotoColeccion.objects.get(pk=foto_coleccion_id)
        try:
            like_foto_coleccion = LikeFotoColeccion.objects.create(usuario=user_comprador, foto_coleccion=foto_coleccion_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el like a la foto de colección")

        return like_foto_coleccion
    '''


class LikeFotoProductoSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_like_fotoproducto')
    foto_producto_id = serializers.IntegerField(required=False, source='foto_like_fotoproducto')

    class Meta:
        model = LikeFotoProducto
        fields = ('username', 'foto_producto_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_foto_producto_id(self, foto_producto_id):
        if not FotoProducto.objects.filter(pk=foto_producto_id).exists():
            raise serializers.ValidationError("La foto del producto no existe")
        return foto_producto_id

    def create(self, validated_data):
        foto_producto_id = self.validated_data['foto_like_fotoproducto']
        username_comprador = self.initial_data['username']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        foto_producto_obj = FotoProducto.objects.get(pk=foto_producto_id)
        try:
            like_foto_producto = LikeFotoProducto.objects.create(usuario=user_comprador, foto_producto=foto_producto_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el like a la foto del producto")

        return like_foto_producto

class LikePostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_like_post')
    post_id = serializers.IntegerField(required=False, source='post_like_post')

    class Meta:
        model = LikePost
        fields = ('username', 'post_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_post_id(self, post_id):
        if not Post.objects.filter(pk=post_id).exists():
            raise serializers.ValidationError("El post no existe")
        return post_id

    def create(self, validated_data):
        post_id = self.validated_data['post_like_post']
        username_comprador = self.validated_data['usuario_like_post']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        post_obj = Post.objects.get(pk=post_id)
        try:
            like_post = LikePost.objects.create(usuario=user_comprador, post=post_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el like al post")

        return like_post

'''
class LikeImagenPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required= False, source='usuario_like_imagenpost')
    imagen_post_id = serializers.IntegerField(required=False, source='imagen_like_imagenpost')

    class Meta:
        model = LikeImagenPost
        fields = ('username', 'imagen_post_id')

    def validate_username(self, username):
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_imagen_post_id(self, imagen_post_id):
        if not ImagenPost.objects.filter(pk=imagen_post_id).exists():
            raise serializers.ValidationError("La imagen del post no existe")
        return imagen_post_id

    def create(self, validated_data):
        imagen_post_id = self.validated_data['imagen_like_imagenpost']
        username_comprador = self.validated_data['usuario_like_imagenpost']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        imagen_post_obj = ImagenPost.objects.get(pk=imagen_post_id)
        try:
            like_imagen_post = LikeImagenPost.objects.create(usuario=user_comprador, imagen_post=imagen_post_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el like a la imagen del post")

        return like_imagen_post
'''

class AvisoFaltaStockSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    id_producto = serializers.IntegerField(required=False)
    nombre_producto = serializers.CharField(required=False)
    talle_id = serializers.IntegerField(required=True)
    talle_desc = serializers.CharField(required=False)

    class Meta:
        model = WishList
        fields = ('id', 'username', 'id_producto', 'nombre_producto', 'talle_id', 'talle_desc')

    def validate_username(self, username):
        #print('entra al validate del username en serializer')
        if not UserComprador.objects.filter(username=username).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username

    def validate_id_producto(self, id_producto):
        #print('entra al validate del producto en serializer')
        id_producto = self.initial_data['id_producto']
        try:
            producto_obj = Producto.objects.get(pk=id_producto)
        except:
            raise serializers.ValidationError("El producto no existe")
        return id_producto

    def validate_talle_id(self, talle_id):
        #print('entra al validate del talle en serializer')
        try:
            articulo_obj = TalleProducto.objects.get(pk=talle_id)
        except:
            raise serializers.ValidationError("El talle no existe")

        if articulo_obj.stock > 1:
            raise serializers.ValidationError("El artículo tiene stock")

        return talle_id

    def create(self, validated_data):
        username_comprador = self.validated_data['username']
        user_comprador = UserComprador.objects.get(username=username_comprador)
        id_producto = self.validated_data['id_producto']
        articulo_id = self.validated_data['talle_id']
        articulo_obj = TalleProducto.objects.get(pk=articulo_id)
        try:
            aviso_stock_obj = AvisoFaltaStock.objects.create(usuario=user_comprador, articulo=articulo_obj)
        except:
            raise serializers.ValidationError("No se pudo agregar el artículo a Avisos de Falta de Stock")

        return aviso_stock_obj


class NotificacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notificacion
        fields = ('id', 'usuario', 'articulo', 'mensaje', 'leida',
                  'archivar', 'leida_fecha', 'archivar_fecha')


class DatosMarcaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Marca
        fields = ('__all__')


class ProcesoBatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcesoBatch
        fields = ('id', 'marca', 'tipo', 'archivo')
        read_only_fields = (
            'procesado', 'procesador_error', 'procesado_error_tipo',
            'procesado_fecha',
        )


class ProcesoBatchErrorSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProcesoBatchError
        fields = '__all__'


class ProductoGestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Producto
        fields = ('id', 'nombre_producto', 'cod_producto', 'descripcion',
                'categoria', 'foto_principal', 'precio', 'porc_descuento',
                'color')

class TalleProductoGestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = TalleProducto
        fields = ('id', 'producto', 'talle', 'shop_sku', 'stock')


class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('nombre_post', 'descripcion')


class ImagenPostGestionSerializer(serializers.ModelSerializer):
    imagen_post = serializers.ImageField(required=True)

    class Meta:
        model = ImagenPost
        fields = ('post', 'imagen_post')


class LocalGestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Local
        fields = ('nombre_local', 'direccion', 'ciudad', 'telefono', 'horario')


class FotoLocalGestionSerializer(serializers.ModelSerializer):
    foto_local = serializers.ImageField(required=True)

    class Meta:
        model = FotoLocal
        fields = ('local', 'foto_local')


class FotoNovedadGestionSerializer(serializers.ModelSerializer):
    foto_novedad = serializers.ImageField(required=True)

    class Meta:
        model = FotoNovedad
        fields = ('novedad', 'foto_novedad')
