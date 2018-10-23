import json
import copy
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.generic import TemplateView
from django.core.urlresolvers import reverse
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (IsAuthenticated)
from rest_framework.response import Response

from .models import Producto, Marca, Combinacion, TalleProducto, Post, \
        ImagenPost, Local, FotoLocal, Novedad, FotoNovedad, ColorProducto, \
        FotoProducto, Foto360Producto

from .serializers import DatosMarcaSerializer, ProductoGestionSerializer, \
        TalleProductoGestionSerializer, PostSerializer, \
        ImagenPostGestionSerializer, LocalGestionSerializer, \
        FotoLocalGestionSerializer, NovedadSerializer, \
        FotoNovedadGestionSerializer
from auth_api.models import UserMarca
from auth_api.serializers import UserMarcaSerializer


class DashboardPedidosView(TemplateView):
    template_name = "mercado_vindu/dashboard_pedidos.html"


class DatosMarcaView(APIView):
    queryset = Marca.objects.all()
    serializer_class = DatosMarcaSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/datos_marca.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')

        serializer = self.serializer_class(marca)
        users_marca = UserMarca.objects.filter(marca=marca)
        return Response({'serializer': serializer,
            'style': self.style,
            'marca': marca,
            'users_marca': users_marca})

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        if marca.logo and not request.data.get('logo'):
            copy = request.data.copy()
            copy['logo'] = marca.logo
            if marca.logo_cuadrado and not request.data.get('logo_cuadrado'):
                copy['logo_cuadrado'] = marca.logo_cuadrado
            serializer = self.serializer_class(marca, data=copy)
        else:
            serializer = self.serializer_class(marca, data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer,
                'style': self.style,
                'marca': marca})
        serializer.save()
        return redirect('datos_marca')


def get_imagen_ppal_por_producto_id(request, producto_id):
    if producto_id:
        producto = Producto.objects.get(pk=producto_id)
        data = {'foto_principal': producto.foto_principal.url}
        return JsonResponse(data)
    else:
        return HttpResponse(status=400)

def PruebaLoginFacebook(request):
    return render(request, 'get_access_token.html', {})


class ListaProductosView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "mercado_vindu/lista_productos.html"
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        queryset = Producto.objects.filter(marca=marca).order_by('-id')
        return Response({'productos': queryset})


class ProductoView(APIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/producto.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            request.user.usermarca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        borrar = kwargs['var'] if 'var' in kwargs else None
        if borrar:
            producto = Producto.objects.get(
                id=kwargs['pk'])
            producto.delete()
            return redirect(reverse('lista_de_productos'))
        if 'pk' in kwargs:
            producto = Producto.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(producto)
        else:
            producto = None
            serializer = self.serializer_class()

        return Response({
            'serializer': serializer,
            'style': self.style,
            'producto': producto,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        if 'otras_fotos' in request.data:
            otras_fotos = [x for x in request.FILES.getlist('otras_fotos')]
        if 'fotos_360' in request.data:
            fotos_360 = [x for x in request.FILES.getlist('fotos_360')]
        if 'pk' in kwargs:
            producto = Producto.objects.get(
                id=kwargs['pk'])
            if producto.foto_principal and not request.data.get('foto'):
                copy = request.data.copy()
                copy['foto'] = producto.foto_principal
                serializer = self.serializer_class(producto, data=copy)
            else:
                serializer = self.serializer_class(producto, data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
        serializer.save()
        nuevo_producto = Producto.objects.get(id=serializer.instance.id)
        if otras_fotos:
            for foto in otras_fotos:
                foto_producto = FotoProducto.objects.create(
                        producto=nuevo_producto,
                        foto_producto=foto,
                        )
        if fotos_360:
            for foto in fotos_360:
                foto_360 = Foto360Producto.objects.create(
                        producto=nuevo_producto,
                        foto360_producto=foto,
                        )

        return redirect(reverse('modificar_producto',
                            kwargs={'pk': nuevo_producto.id}))


class CopiarProductoView(APIView):
    queryset = Producto.objects.all()
    serializer_class = ProductoGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/producto.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        producto = Producto.objects.get(
            id=kwargs['pk'])

        producto_copia = copy.copy(producto)
        producto_copia.id = None
        producto_copia.save()

        # copia otros colores
        qs_otros_colores = producto.color_producto_original.all()

        for otro_color in qs_otros_colores:
            otro_color_copia = ColorProducto.objects.create(producto=producto_copia, otro_color=otro_color.otro_color)

        # copia combinaciones
        qs_combinacion = producto.rel_producto_original.all()

        for combinacion in qs_combinacion:
            combinacion_copia = Combinacion.objects.create(producto=producto_copia, combina_con=combinacion.combina_con)

        # copia talles y stocks
        qs_talles = TalleProducto.objects.filter(producto=producto).order_by('id')

        for talle in qs_talles:
            talle_copia = copy.copy(talle)
            talle_copia.id = None
            talle_copia.producto = producto_copia
            talle_copia.save()

        return redirect(reverse('modificar_producto',
                            kwargs={'pk': producto_copia.id}))


class CombinacionView(APIView):
    serializer_class = ProductoGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/combinacion.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            request.user.usermarca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        producto = Producto.objects.get(
            id=kwargs['pk'])
        serializer = ProductoGestionSerializer()
        return Response({
            'serializer': serializer,
            'style': self.style,
            'producto': producto,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        producto = Producto.objects.get(
            id=kwargs['pk'])
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
        serializer.save()
        nuevo_producto = Producto.objects.get(id=serializer.instance.id)
        Combinacion.objects.create(
                producto=producto,
                combina_con=nuevo_producto)

        return redirect(reverse('modificar_producto',
                            kwargs={'pk': producto.id}))


class StockView(APIView):
    serializer_class = TalleProductoGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "mercado_vindu/stock.html"
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        productos = [x for x in Producto.objects.all().order_by('-id') if x.get_stock()]
        return Response({'productos': productos})


class TalleProductoView(APIView):
    serializer_class = TalleProductoGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/talle_producto.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        var = kwargs['var'] if 'var' in kwargs else None
        if 'pk' in kwargs:
            talle_producto = TalleProducto.objects.get(
                id=kwargs['pk'])
            producto = talle_producto.producto.id
            serializer = self.serializer_class(talle_producto)
        else:
            producto = Producto.objects.get(
                id=kwargs['id_producto'])
            talle_producto = None
            serializer = self.serializer_class()

        return Response({
            'serializer': serializer,
            'style': self.style,
            'producto': producto,
            'talle_producto': talle_producto,
            'var': var,
            })

    def post(self, request, *args, **kwargs):
        if 'talle_id' in request.data and request.is_ajax():
            talle_producto_id = request.data.get('talle_id')
            stock = request.data.get('stock')
            shop_sku = request.data.get('shop_sku')
            talle_producto = TalleProducto.objects.get(
                id=talle_producto_id)
            producto = talle_producto.producto
            copy = request.data.copy()
            copy['producto'] = producto.id
            copy['talle'] = talle_producto.talle
            copy['shop_sku'] = shop_sku if shop_sku else ' '
            copy['stock'] = stock if stock else 0
            serializer = self.serializer_class(talle_producto, data=copy)
            if not serializer.is_valid():
                return HttpResponse(json.dumps({'message': str(serializer.errors)}),
                    content_type='application/json')
            else:
                serializer.save()
                return HttpResponse(json.dumps({'message': 'ok'}),
                    content_type='application/json')
        else:
            producto = Producto.objects.get(
                id=kwargs['id_producto'])
            copy = request.data.copy()
            copy['producto'] = producto.id
            serializer = self.serializer_class(data=copy)
            if not serializer.is_valid():
                return Response({'serializer': serializer, 'style': self.style})
            serializer.save()
            return redirect('stock')

        return redirect('stock')


class PosteosView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "mercado_vindu/posteos.html"
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        queryset = Post.objects.filter(marca=marca).order_by('-id')
        return Response({'posteos': queryset})


class PosteoView(APIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/posteo.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            request.user.usermarca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        if 'pk' in kwargs:
            post = Post.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(post)
            imagen_serializer = ImagenPostGestionSerializer()
        else:
            post = None
            serializer = self.serializer_class()
            imagen_serializer = ImagenPostGestionSerializer()

        return Response({
            'serializer': serializer,
            'imagen_serializer': imagen_serializer,
            'style': self.style,
            'post': post,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        imagen = None
        if 'imagen_post' in request.data:
            imagen = request.data.get('imagen_post')
        if 'pk' in kwargs:
            post = Post.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(post, data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        else:
            serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
            serializer.save()
            nuevo_post = Post.objects.get(id=serializer.instance.id)
            if imagen:
                ImagenPost.objects.create(
                    post=nuevo_post,
                    imagen_post=imagen)

            return redirect(reverse('modificar_posteo',
                                    kwargs={'pk': nuevo_post.id}))


class ImagenPosteoView(APIView):
    queryset = ImagenPost.objects.all()
    serializer_class = ImagenPostGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/posteo.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        imagen_posteo = ImagenPost.objects.get(id=kwargs['id_imagen'])
        posteo = Post.objects.get(id=kwargs['id_posteo'])
        imagen_posteo.delete()

        return redirect(reverse('modificar_posteo',
                        kwargs={'pk': posteo.id}))


class LocalesView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "mercado_vindu/locales.html"
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')

        queryset = Local.objects.filter(marca=marca).order_by('-id')
        return Response({'locales': queryset})


class LocalView(APIView):
    queryset = Local.objects.all()
    serializer_class = LocalGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/local.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            request.user.usermarca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        borrar = kwargs['var'] if 'var' in kwargs else None
        if borrar:
            local = Local.objects.get(
                id=kwargs['pk'])
            local.delete()
            return redirect(reverse('locales'))
        if 'pk' in kwargs:
            local = Local.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(local)
            imagen_serializer = FotoLocalGestionSerializer()
        else:
            local = None
            serializer = self.serializer_class()
            imagen_serializer = FotoLocalGestionSerializer()

        return Response({
            'serializer': serializer,
            'imagen_serializer': imagen_serializer,
            'style': self.style,
            'local': local,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        imagen = None
        if 'foto_local' in request.data:
            imagen = request.data.get('foto_local')
        if 'pk' in kwargs:
            local = Local.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(local, data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        else:
            serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
            serializer.save()
            nuevo_local = Local.objects.get(id=serializer.instance.id)
            if imagen:
                FotoLocal.objects.create(
                    local=nuevo_local,
                    foto_local=imagen)

            return redirect(reverse('modificar_local',
                                    kwargs={'pk': nuevo_local.id}))

class FotoLocalView(APIView):
    queryset = FotoLocal.objects.all()
    serializer_class = FotoLocalGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/local.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        foto_local = FotoLocal.objects.get(id=kwargs['id_foto'])
        local = Local.objects.get(id=kwargs['id_local'])
        foto_local.delete()

        return redirect(reverse('modificar_local',
                        kwargs={'pk': local.id}))


class NovedadesView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = "mercado_vindu/novedades.html"
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        queryset = Novedad.objects.filter(marca=marca).order_by('-id')
        return Response({'novedades': queryset})


class NovedadView(APIView):
    queryset = Novedad.objects.all()
    serializer_class = NovedadSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/novedad.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            request.user.usermarca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')
        borrar = kwargs['var'] if 'var' in kwargs else None
        if borrar:
            novedad = Novedad.objects.get(
                id=kwargs['pk'])
            novedad.delete()
            return redirect(reverse('novedades'))
        if 'pk' in kwargs:
            novedad = Novedad.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(novedad)
            imagen_serializer = FotoNovedadGestionSerializer()
        else:
            novedad = None
            serializer = self.serializer_class()
            imagen_serializer = FotoNovedadGestionSerializer()

        return Response({
            'serializer': serializer,
            'imagen_serializer': imagen_serializer,
            'style': self.style,
            'novedad': novedad,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        imagen = None
        if 'foto_novedad' in request.data:
            imagen = request.data.get('foto_novedad')
        if 'pk' in kwargs:
            novedad = Novedad.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(novedad, data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        else:
            serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
            serializer.save()
            nueva_novedad = Novedad.objects.get(id=serializer.instance.id)
            if imagen:
                FotoNovedad.objects.create(
                    novedad=nueva_novedad,
                    foto_novedad=imagen)

            return redirect(reverse('modificar_novedad',
                                    kwargs={'pk': nueva_novedad.id}))


class FotoNovedadView(APIView):
    queryset = FotoNovedad.objects.all()
    serializer_class = FotoLocalGestionSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/novedad.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        foto_novedad = FotoNovedad.objects.get(id=kwargs['id_foto'])
        novedad = Novedad.objects.get(id=kwargs['id_novedad'])
        foto_novedad.delete()
        return redirect(reverse('modificar_novedad',
                        kwargs={'pk': novedad.id}))


class UserMarcaView(APIView):
    queryset = UserMarca.objects.all()
    serializer_class = UserMarcaSerializer
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'mercado_vindu/user_marca.html'
    permission_classes = (IsAuthenticated,)
    style = {'template_pack': 'rest_framework/vertical/'}

    def get(self, request, *args, **kwargs):
        try:
            marca = request.user.usermarca.marca
        except:
            # Si no es usuario marca, reenvía al admin
            return redirect('/admin')

        if 'pk' in kwargs:
            user_marca = UserMarca.objects.get(
                id=kwargs['pk'])
            serializer = self.serializer_class(user_marca)
        else:
            user_marca = None
            serializer = self.serializer_class()

        return Response({
            'serializer': serializer,
            'style': self.style,
            'user_marca': user_marca,
            })

    def post(self, request, *args, **kwargs):
        marca = request.user.usermarca.marca
        if 'pk' in kwargs:
            user_marca = UserMarca.objects.get(
                id=kwargs['pk'])
            if user_marca.foto_avatar and not request.data.get('foto_avatar'):
                copy = request.data.copy()
                copy['foto_avatar'] = user_marca.foto_avatar
                serializer = self.serializer_class(user_marca, data=copy)
            else:
                serializer = self.serializer_class(user_marca, data=request.data)
        else:
            serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({'serializer': serializer, 'style': self.style})
        serializer.validated_data['marca'] = Marca.objects.get(id=marca.id)
        serializer.save()
        nuevo_usuario = UserMarca.objects.get(id=serializer.instance.id)
        return redirect('/')



