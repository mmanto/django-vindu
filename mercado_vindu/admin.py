from django.contrib import admin
from mercado_vindu.models import *
from mercado_vindu.forms import *
from auth_api.models import UserMarca, UserComprador
from django.utils.html import format_html
import copy
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline


class TablaTallesAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_prenda', 'segmento_sexo', 'display_imagen_talles')
    list_display_links = ('id',) 
    readonly_fields = ('id',)
    ordering = ('segmento_sexo', 'tipo_prenda')

    def display_imagen_talles(self, obj):
        if obj.imagen_talles:
            return format_html('<img src="{}" width=100px />'.format(obj.imagen_talles.url))
        else:
            return ''

    display_imagen_talles.short_description = 'Imagen de Talles'

  

class ClaseMarcaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', )
    list_display_links = ('nombre',) 
    ordering = ('nombre',)


class DepositoAdminInline(admin.TabularInline):
    model = Deposito
    form  = DepositoAdminForm
    formset = DepositoAdminFormset
    extra = 1

class MarcaAdmin(admin.ModelAdmin):
    form = MarcaAdminForm
    inlines = [DepositoAdminInline,]

    fieldsets = (
        ('Datos Generales', {
            'fields': ('nombre', 'razon_social', 'logo', 'logo_cuadrado', 'mail_contacto', 'descripcion', 'sitio_web', 'clase_marca', 'porcentaje_vindu')
        }),
        ('Datos de Proveedores de Pagos', {
             'fields': ('proveedor_pago', 'mp_client_id', 'mp_client_secret','pu_api_key', 'pu_api_login', 'pu_account_id', 'pu_merchand_id')
        }),
        ('Datos Fiscales e Impositivos', {
             'fields': ('domicilio_fiscal', 'cuit_nro', 'condicion_iva', 'agente_ret_ib',
                        'agente_ret_gan', 'agente_ret_iva')
        }),
        ('Otros Datos para el Dashboard de Marcas', {
             'fields': ('responsable_ventas', 'telefono_contacto', 'responsable_cobranzas', 'localidad', 'provincia',
                        'codigo_postal')
        }),
        ('Datos Bancarios', {
             'fields': ('nro_cuenta', 'cbu', )
        }),
        ('Otros Datos', {
             'fields': ('ind_marca_activa', 'valor_promocion_envio', 'date_updated', 'contrato_firmado', 'terminos')
        }),
    )

    '''
        ('Domicilio del depósito', {
             'fields': ('responsable_deposito', 'telefono_responsable', 'calle', 'numero', 'piso',
             'departamento', 'provincia', 'localidad', 'codigo_postal', 'api_id_envio_pack')
        }), 
    '''    

    def display_logo(self, obj):
        return format_html('<img src="{}" width=100px />'.format(obj.logo.url))

    display_logo.short_description = 'Logo'

    list_display = ('nombre', 'display_logo', 'descripcion', 'sitio_web', 'clase_marca', 'date_created', 'date_updated')
    list_display_links = ('nombre',) 
    readonly_fields = ('date_created', 'date_updated')
    search_fields = ['nombre',]
    ordering = ('nombre',)

    def get_readonly_fields(self, request, obj=None):
        # Un Usuario Marca no puede cambiar el % de comisión Vindu, sólo verlo
        if not request.user.is_superuser:
            if obj: # editing an existing object
                return self.readonly_fields + ('porcentaje_vindu', 'ind_marca_activa')
        return self.readonly_fields

    def get_queryset(self, request):
        qs_marcas = super(MarcaAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_marcas = qs_marcas.filter(id=user.marca.id)
        return qs_marcas

class CategoriaAdmin(admin.ModelAdmin):
    form = CategoriaAdminForm

    list_display = ('id', 'nombre', 'categoria_padre', 'display_imagen')
    list_display_links = ('nombre',) 
    readonly_fields = ('id',)
    search_fields = ['nombre',]
    ordering = ('-id', )

    def display_imagen(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width=100px />'.format(obj.imagen.url))
        else:
            return ''

    display_imagen.short_description = 'Imagen de Categoría'


'''
class FotoColeccionInline(admin.StackedInline):
    model = FotoColeccion
    form  = FotoColeccionAdminForm
    extra = 1

class ColeccionAdmin(admin.ModelAdmin):
    form = ColeccionAdminForm
    inlines = [FotoColeccionInline,]

    list_display = ('nombre_coleccion', 'marca', 'descripcion', 'date_created', 'date_updated')
    list_display_links = ('nombre_coleccion',) 
    search_fields = ['nombre_coleccion', 'marca']
    readonly_fields = ('date_created', 'date_updated')
    ordering = ('marca','-date_updated', 'nombre_coleccion')

    def get_form(self, request, obj=None, **kwargs):
        form = super(ColeccionAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs_colecciones = super(ColeccionAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_colecciones = qs_colecciones.filter(marca=user.marca)
        return qs_colecciones
'''

class FotoLocalInline(admin.StackedInline):
    model = FotoLocal
    form  = FotoLocalAdminForm
    extra = 1

class LocalAdmin(admin.ModelAdmin):
    form = LocalAdminForm
    inlines = [FotoLocalInline,]

    list_display = ('nombre_local', 'marca', 'direccion', 'ciudad', 'date_created', 'date_updated')
    list_display_links = ('nombre_local',) 
    search_fields = ['nombre_local', 'marca']
    readonly_fields = ('cant_calificaciones', 'suma_calificaciones')
    ordering = ('marca','-date_updated', 'nombre_local')

    def get_form(self, request, obj=None, **kwargs):
        form = super(LocalAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs_locales = super(LocalAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_locales = qs_locales.filter(marca=user.marca)
        return qs_locales

class ColorProductoInline(NestedTabularInline):
    model = ColorProducto
    form  = ColorProductoAdminForm
    extra = 1
    fk_name = 'producto'
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        return format_html('<img src="{}" width=100px />'.format(obj.otro_color.foto_principal.url))

    image_tag.short_description = 'Imagen del Producto en Otro Color'

    def get_parent_object_from_request(self, request):
        """
        Returns the parent object from the request or None.

        Note that this only works for Inlines, because the `parent_model`
        is not available in the regular admin.ModelAdmin as an attribute.
        """
        from django.core.urlresolvers import resolve
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "otro_color":
            producto_padre = self.get_parent_object_from_request(request)
            #print ('producto_padre: ', producto_padre)
            if producto_padre:
                kwargs["queryset"] = Producto.objects.filter(marca=producto_padre.marca, categoria=producto_padre.categoria).exclude(pk=producto_padre.id)
                return db_field.formfield(**kwargs)
        return super(ColorProductoInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class TalleProductoInline(NestedStackedInline):
    model = TalleProducto
    form  = TalleProductoAdminForm
    extra = 0

class FotoProductoInline(NestedStackedInline):
    model = FotoProducto
    form  = FotoProductoAdminForm
    extra = 1

class TomaFoto360Inline(NestedTabularInline):
    model = TomaFoto360
    form  = TomaFoto360AdminForm
    extra = 0
    ordering = ('pk',)

class Foto360ProductoInline(NestedTabularInline):
    model = Foto360Producto
    form  = Foto360ProductoAdminForm
    inlines = [TomaFoto360Inline, ]
    extra = 0

class ImagenPostAdminInline(admin.StackedInline):
    model = ImagenPost
    form  = ImagenPostAdminForm
    extra = 1

class VideoLinkPostAdminInline(admin.StackedInline):
    model = VideoLinkPost
    #form  = ImagenPostAdminForm
    extra = 1

class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    inlines = [ImagenPostAdminInline, VideoLinkPostAdminInline]

    list_display = ('nombre_post', 'marca', 'descripcion', 'date_created', 'date_updated')
    list_display_links = ('nombre_post',) 
    search_fields = ['nombre_post', 'marca']
    readonly_fields = ('date_created', 'date_updated')
    ordering = ('marca','-date_updated', 'nombre_post')

    def get_form(self, request, obj=None, **kwargs):
        form = super(PostAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs_posts = super(PostAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_posts = qs_posts.filter(marca=user.marca)
        return qs_posts


class CombinacionProductoInline(NestedTabularInline):
    model = Combinacion
    form  = CombinacionAdminForm
    extra = 1
    fk_name = 'producto'
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        return format_html('<img src="{}" width=100px />'.format(obj.combina_con.foto_principal.url))

    image_tag.short_description = 'Imagen Producto Combinado'

    def get_parent_object_from_request(self, request):
        """
        Returns the parent object from the request or None.

        Note that this only works for Inlines, because the `parent_model`
        is not available in the regular admin.ModelAdmin as an attribute.
        """
        from django.core.urlresolvers import resolve
        resolved = resolve(request.path_info)
        if resolved.args:
            return self.parent_model.objects.get(pk=resolved.args[0])
        return None

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "combina_con":
            producto_padre = self.get_parent_object_from_request(request)
            #print ('producto_padre: ', producto_padre)
            if producto_padre:
                kwargs["queryset"] = Producto.objects.filter(marca=producto_padre.marca).exclude(pk=producto_padre.id)
                return db_field.formfield(**kwargs)
        return super(CombinacionProductoInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


def copiar_producto(modeladmin, request, queryset):
    for producto in queryset:
        producto_copia = copy.copy(producto) # django copy object
        producto_copia.id = None   # set 'id' to None to create new object
        producto_copia.save()    # initial save

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
            talle_copia = copy.copy(talle) # django copy object
            talle_copia.id = None   # set 'id' to None to create new object
            talle_copia.producto = producto_copia
            talle_copia.save()

    copiar_producto.short_description = "Copiar Producto"


class ProductoAdmin(NestedModelAdmin):
    form = ProductoAdminForm
    inlines = [ColorProductoInline, TalleProductoInline, FotoProductoInline, Foto360ProductoInline, CombinacionProductoInline]

    list_display = ('id', 'nombre_producto', 'marca', 'categoria', 'coleccion', 'precio', 'date_created', 'date_updated')
    list_display_links = ('nombre_producto',) 
    search_fields = ['nombre_producto', 'categoria__nombre']
    readonly_fields = ('date_created', 'date_updated', 'foto_principal_optim', 'foto_principal_thumb')
    ordering = ('marca', '-date_updated', 'nombre_producto', )
    list_filter = ('marca', 'categoria', )
    actions = [copiar_producto]

    class Media:
        js = (
            'admin/js/producto_admin_script.js',   # app static folder
        )

    '''
    def get_readonly_fields(self, request, obj=None):
        current_user = request.user
        if current_user.is_staff and not current_user.is_superuser:
            return self.readonly_fields + ('imagen_talles',)
        return self.readonly_fields
    '''

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProductoAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form


    def get_queryset(self, request):
        qs_productos = super(ProductoAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque la marca está en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_productos = qs_productos.filter(marca=user.marca)
        return qs_productos

class FotoNovedadInline(admin.StackedInline):
    model = FotoNovedad
    form  = FotoNovedadAdminForm
    extra = 1

class NovedadAdmin(admin.ModelAdmin):
    form = NovedadAdminForm
    inlines = [FotoNovedadInline,]

    list_display = ('titulo_novedad', 'marca', 'descripcion', 'date_created', 'date_updated')
    list_display_links = ('titulo_novedad',) 
    search_fields = ['titulo_novedad', 'marca']
    readonly_fields = ('date_created', 'date_updated')
    ordering = ('marca','-date_updated', 'titulo_novedad')

    def get_form(self, request, obj=None, **kwargs):
        form = super(NovedadAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs_novedades = super(NovedadAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_novedades = qs_novedades.filter(marca=user.marca)
        return qs_novedades

class UsuarioSeguidorMarcaAdmin(admin.ModelAdmin):
    model = MarcaSeguida
    form  = UsuarioSeguidorMarcaAdminForm
    fields = ('nombre', 'apellido', 'username')
    list_display = ('nombre', 'apellido', 'username',)
    readonly_fields = ('nombre', 'apellido', 'username')
    extra = 0

    def nombre(self, obj):
        return obj.usuario.first_name

    def apellido(self, obj):
        return obj.usuario.last_name

    def username(self, obj):
        return obj.usuario.username

    def get_queryset(self, request):
        qs_usuarios_seguidores = super(UsuarioSeguidorMarcaAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
           # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
           user = UserMarca.objects.get(username=request.user.username)
           qs_marcas = Marca.objects.filter(id=user.marca.id)
           qs_usuarios_seguidores = qs_usuarios_seguidores.filter(marca__in=qs_marcas)
        return qs_usuarios_seguidores


class NotificacionAdmin(admin.ModelAdmin):
    model = Notificacion

class ProcesoBatchAdmin(admin.ModelAdmin):
    model = ProcesoBatch
    list_display = ('id', 'marca', 'tipo', 'archivo', 'procesado', 'procesado_error', 'date_created', )
    readonly_fields = ('procesado', 'procesado_error', 'procesado_error_tipo', 'procesado_fecha',
                       'date_created', 'date_updated')
    ordering = ('-date_created',)
    list_display_links = ('id',) 


admin.site.register(TablaTalles, TablaTallesAdmin)
admin.site.register(Marca, MarcaAdmin)
admin.site.register(Categoria, CategoriaAdmin)
#admin.site.register(Coleccion, ColeccionAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Local, LocalAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Novedad, NovedadAdmin)
admin.site.register(MarcaSeguida, UsuarioSeguidorMarcaAdmin)
admin.site.register(ClaseMarca, ClaseMarcaAdmin)
admin.site.register(Notificacion, NotificacionAdmin)
admin.site.register(ProcesoBatch, ProcesoBatchAdmin)