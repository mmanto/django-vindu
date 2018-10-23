from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from .api import CategoriaViewSet, MarcaViewSet, MarcaAllViewSet, MarcaCategoriaLogViewSet, \
             FiltrosCategoriasMarcaViewSet, ProductosAdminByMarcaCategoriaViewSet, AgregarWishListViewSet, \
             MarcaSeguidaViewSet, GetMarcasSeguidasViewSet, WishListViewSet, \
             GetWishListViewSet, GetPerfilMarcaViewSet, MarcaLogViewSet, BuscadorGenericoViewSet, \
             GetDetallePerfilPropioViewSet, GetDetallePerfilOtroViewSet, LocalesLogViewSet, \
             NovedadesLogViewSet, OfertasMarcaLogViewSet, DescuentosViewSet, DetalleProductoViewSet, \
             LikeFotoProductoViewSet, VidrieraViewSet, DetallePostViewSet, \
             ProductosCombAdminByMarcaCategoriaViewSet, ImagenesBuscadorViewSet, \
             DescuentosCategoriaViewSet, OfertasMarcaCategoriaLogViewSet, AvisoFaltaStockViewSet, \
             NotificacionViewSet, ProcesoBatchViewSet, ProcesoBatchErrorViewSet, \
             GetProductoActualizacionPrecioDescuentoCSV, \
             GetProductoActualizacionStockCSV, LikePostViewSet

from .views import DatosMarcaView, ListaProductosView, ProductoView, \
    CopiarProductoView, CombinacionView, StockView, TalleProductoView, PosteosView, \
    PosteoView, ImagenPosteoView, LocalesView, LocalView, FotoLocalView, \
    NovedadesView, NovedadView, FotoNovedadView, UserMarcaView


router = DefaultRouter()
router.register(r'^get-all-categorias', CategoriaViewSet)
router.register(r'^get-marcas', MarcaViewSet)
router.register(r'^get-all-marca/(?P<marca_id>\d+)', MarcaAllViewSet)
#router.register(r'^get-detalle-producto/(?P<producto_id>\d+)', DetalleProductoViewSet)
#router.register(r'^get-productos-oferta', ProductosOfertaViewSet)
router.register(r'^get-filtros-categorias-marca/(?P<marca_id>\d+)', FiltrosCategoriasMarcaViewSet)
#router.register(r'^get-admin-productos-by-marca_id/(?P<marca_id>\d+)', ProductosAdminByMarcaViewSet)
router.register(r'^get-admin-productos-by-marca-categoria_id/(?P<marca_id>\d+)/(?P<categoria_id>\d+)', ProductosAdminByMarcaCategoriaViewSet)
router.register(r'^get-admin-comb-productos-by-marca-categoria_id/(?P<marca_id>\d+)/(?P<categoria_id>\d+)', ProductosCombAdminByMarcaCategoriaViewSet)
#router.register(r'^set_marca_favorita', ensure_csrf_cookie(MarcaFavoritaViewSet)
router.register(r'^marca_seguida', MarcaSeguidaViewSet)
router.register(r'^get-marcas-seguidas', GetMarcasSeguidasViewSet)
#router.register(r'^producto_favorito', ProductoFavoritoViewSet)
#router.register(r'^wishlist/(?P<producto_id>\d+)/(?P<talle>\w+)', WishListViewSet)
router.register(r'^agregar-wishlist/(?P<articulo_id>\d+)', AgregarWishListViewSet),
router.register(r'^wishlist-detail', WishListViewSet),
router.register(r'^get-wishlist', GetWishListViewSet)
router.register(r'^get-perfil-marca/(?P<marca_id>\d+)', GetPerfilMarcaViewSet)
router.register(r'^get-productos-by-marca_id/(?P<marca_id>\d+)', MarcaLogViewSet)
router.register(r'^get-productos-by-marca-categoria_id/(?P<marca_id>\d+)/(?P<categoria_id>\d+)', MarcaCategoriaLogViewSet)
router.register(r'^get-locales-by-marca_id/(?P<marca_id>\d+)', LocalesLogViewSet)
router.register(r'^get-novedades-by-marca_id/(?P<marca_id>\d+)', NovedadesLogViewSet)
router.register(r'^get-ofertas-by-marca_id/(?P<marca_id>\d+)', OfertasMarcaLogViewSet)
router.register(r'^get-ofertas-by-marca-categoria_id/(?P<marca_id>\d+)/(?P<categoria_id>\d+)', OfertasMarcaCategoriaLogViewSet)
router.register(r'^get-descuentos', DescuentosViewSet)
router.register(r'^get-descuentos-by-categoria_id/(?P<categoria_id>\d+)', DescuentosCategoriaViewSet)
router.register(r'^get-detalle-producto/(?P<producto_id>\d+)', DetalleProductoViewSet)
router.register(r'^get-detalle-post/(?P<post_id>\d+)', DetallePostViewSet)
router.register(r'^buscador', BuscadorGenericoViewSet, 'producto-list')
router.register(r'^get-detalle-mi-perfil', GetDetallePerfilPropioViewSet)
router.register(r'^get-perfil-usuario/(?P<username>\w+)', GetDetallePerfilOtroViewSet)
router.register(r'^get-vidriera', VidrieraViewSet, 'imagenes-post-list')
#router.register(r'^like-coleccion', LikeColeccionViewSet)
router.register(r'^like-post', LikePostViewSet)
#router.register(r'^like-foto-coleccion', LikeFotoColeccionViewSet)
router.register(r'^like-foto-producto', LikeFotoProductoViewSet)
#router.register(r'^like-imagen-post', LikeImagenPostViewSet)
router.register(r'^get-imagenes-buscador', ImagenesBuscadorViewSet, 'imagenes-list')
router.register(r'^aviso_falta_stock/(?P<talle_id>\d+)', AvisoFaltaStockViewSet)
router.register(r'^notificaciones', AvisoFaltaStockViewSet)
router.register(r'^procesos-batch', ProcesoBatchViewSet)
router.register(r'^procesos-batch-errores', ProcesoBatchErrorViewSet)

urlpatterns = [
    url(r'^$', DatosMarcaView.as_view(), name="datos_marca"),
    url(r'^agregar-producto/$', ProductoView.as_view(), name="agregar_producto"),
    url(r'^modificar-producto/(?P<pk>[0-9]+)/$', ProductoView.as_view(), name="modificar_producto"),
    url(r'^borrar-producto/(?P<pk>[0-9]+)/(?P<var>\w*)$', ProductoView.as_view(), name="borrar_producto"),
    url(r'^copiar-producto/(?P<pk>[0-9]+)/$', CopiarProductoView.as_view(), name="copiar_producto"),
    url(r'^combinacion-producto/(?P<pk>[0-9]+)/$', CombinacionView.as_view(), name="combinacion_producto"),
    url(r'^lista-de-productos/$', ListaProductosView.as_view(), name="lista_de_productos"),
    url(r'^get-archivo-actualizacion-precio-descuento', GetProductoActualizacionPrecioDescuentoCSV.as_view(), name="get_archivo_precio_descuento"),
    url(r'^get-archivo-actualizacion-stock', GetProductoActualizacionStockCSV.as_view(), name="get_archivo_stock"),
    url(r'^stock/$', StockView.as_view(), name="stock"),
    url(r'^agregar-talle-producto/(?P<id_producto>\d*)/(?P<var>\w*)$', TalleProductoView.as_view(), name="agregar_talle_producto"),
    url(r'^modificar-talle-producto/(?P<pk>[0-9]+)/$', csrf_exempt(TalleProductoView.as_view()), name="modificar_talle_producto"),
    url(r'^posteos/$', PosteosView.as_view(), name="posteos"),
    url(r'^agregar-posteo/$', PosteoView.as_view(), name="agregar_posteo"),
    url(r'^modificar-posteo/(?P<pk>[0-9]+)/$', PosteoView.as_view(), name="modificar_posteo"),
    url(r'^borrar-imagen-posteo/(?P<id_posteo>\d*)/(?P<id_imagen>\d*)/$', ImagenPosteoView.as_view(), name='borrar_imagen_posteo'),
    url(r'^locales/$', LocalesView.as_view(), name="locales"),
    url(r'^agregar-local/$', LocalView.as_view(), name="agregar_local"),
    url(r'^modificar-local/(?P<pk>[0-9]+)/$', LocalView.as_view(), name="modificar_local"),
    url(r'^modificar-local/(?P<pk>[0-9]+)/$', LocalView.as_view(), name="modificar_local"),
    url(r'^borrar-local/(?P<pk>[0-9]+)/(?P<var>\w*)$', LocalView.as_view(), name="borrar_local"),
    url(r'^borrar-foto-local/(?P<id_local>\d*)/(?P<id_foto>\d*)/$', FotoLocalView.as_view(), name='borrar_foto_local'),
    url(r'^novedades/$', NovedadesView.as_view(), name="novedades"),
    url(r'^agregar-novedad/$', NovedadView.as_view(), name="agregar_novedad"),
    url(r'^modificar-novedad/(?P<pk>[0-9]+)/$', NovedadView.as_view(), name="modificar_novedad"),
    url(r'^borrar-novedad/(?P<pk>[0-9]+)/(?P<var>\w*)', NovedadView.as_view(), name="borrar_novedad"),
    url(r'^borrar-foto-novedad/(?P<id_novedad>\d*)/(?P<id_foto>\d*)/$', FotoNovedadView.as_view(), name='borrar_foto_novedad'),

    url(r'^agregar-usuario-marca/$', UserMarcaView.as_view(), name="agregar_usermarca"),
    url(r'^modificar-usuario-marca/(?P<pk>[0-9]+)/$', UserMarcaView.as_view(), name="modificar_usermarca"),
]

urlpatterns += router.urls
