# -*- encoding: utf-8 -*-
from django.db import models
from datetime import date
from django.core.exceptions import ValidationError

#from auth_api.models import UserComprador
import auth_api
import datetime
from decimal import *

from .helpers import user_directory_path
from django.utils.encoding import smart_text
from core.utils import ContentTypeRestrictedImageField, ContentTypeRestrictedFileField, \
                       generate_optim_picture, generate_thumb_picture
from django.conf import settings
from embed_video.fields import EmbedVideoField
from taggit.managers import TaggableManager


SEGMENTO_EDAD = (
    ('ADULTO', 'Adulto'),
    ('NIÑO12',  'Niño de 9 a 12 años'),
    ('NIÑO5',   'Niño de 5 a 8 años'),
    ('BEBE', 'Hasta 4 años')
)
SEGMENTO_SEXO = (
    ('HOMBRE', 'Hombre'),
    ('MUJER',  'Mujer')
)
TIPO_PRENDA = (
    ('PS', 'Prenda superior'),
    ('PI', 'Prenda inferior'),
    ('CA', 'Calzado')
)
ARCHIVO_BATCH_TIPOS = (
    ('precio', 'precio'),
    ('stock', 'stock')
)
ARCHIVO_BATCH_ERROR_TIPOS = (
    ('archivo', 'Archivo'),
    ('registro', 'Registro'),
)
CONDICION_IVA = (
    ('RI', 'Responsable Inscripto'),
    ('RN', 'Responsable No Inscripto'),
    ('MO', 'Monotributista'),
    ('EX', 'Exento'),
)


def validate_non_negative(value):
    if value < 0:
        raise ValidationError(
            _('Este campo no puede ser negativo')
        )

def validate_positive(value):
    if value <= 0:
        raise ValidationError(
            _('Este campo debe ser mayor que cero')
        )

def validate_percentaje(value):
    if value < 0 or value > 100:
        raise ValidationError(
            _('Este campo debe ser un número entre 0 y 100')
        )

class TablaTalles(models.Model):
    tipo_prenda = models.CharField('Tipo de prenda', max_length=2, choices=TIPO_PRENDA)
    segmento_sexo = models.CharField('Género', max_length=15, choices=SEGMENTO_SEXO, default='HOMBRE')
    imagen_talles = models.ImageField('Imagen de Talles', upload_to='images/tabla_talles')


    class Meta:
        verbose_name = "Tabla de Talles"
        verbose_name_plural = "Tablas de Talles"
        unique_together = ("tipo_prenda", "segmento_sexo")

    def __str__(self):
        return u'%s - %s' % (self.tipo_prenda, self.segmento_sexo)




class ClaseMarca(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField('Descripción', max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = "Clase de Marca"
        verbose_name_plural = "Clases de Marca"

    def __str__(self):
        return u'%s' % (self.nombre)

class Marca(models.Model):
    nombre = models.CharField('Nombre de Fantasía', max_length=100)
    razon_social = models.CharField('Razón Social', max_length=100, blank=True, null=True)
    logo = models.ImageField('Logo formato banner',
                              help_text="Imagen con proporción ancho:alto = 1:0.2037",
                              upload_to='images/logos')
    logo_cuadrado = models.ImageField('Logo formato cuadrado', 
                                       help_text="Logo con alto igual a ancho",
                                       upload_to='images/logos', blank=True, null=True)
    mail_contacto = models.EmailField('Mail de contacto', blank=True, default=None, null=True)
    descripcion = models.CharField('Descripción', max_length=100, blank=True, null=True)
    sitio_web = models.CharField('Sitio web', max_length=50, blank=True, null=True)
    clase_marca = models.ForeignKey(ClaseMarca, on_delete=models.CASCADE, blank=True, null=True)
    porcentaje_vindu = models.DecimalField('Porcentaje comisión Vindu', max_digits=5, decimal_places=2, default=10)
    # Datos fiscales e impositivos
    domicilio_fiscal = models.CharField('Domicilio Fiscal', max_length=100, blank=True, null=True)
    cuit_nro = models.CharField('Cuit Nro', max_length=50, blank=True, null=True)
    condicion_iva = models.CharField('Condición ante el IVA', max_length=2, choices=CONDICION_IVA, default='RI')
    agente_ret_ib = models.BooleanField('Agente de retención de Ingresos Brutos', default=False)
    agente_ret_gan = models.BooleanField('Agente de retención de Ganancias', default=False)
    agente_ret_iva = models.BooleanField('Agente de retención de IVA', default=False)

    # Otros datos para el Dashboard de Marcas
    responsable_ventas = models.CharField('Responsable de ventas', max_length=100, blank=True, null=True)
    responsable_cobranzas = models.CharField('Responsable de cobranzas', max_length=100, blank=True, null=True)
    localidad = models.CharField('Localidad', max_length=50, blank=True, null=True)
    provincia = models.CharField('Provincia', max_length=50, blank=True, null=True)
    codigo_postal = models.CharField('Código Postal', max_length=10, blank=True, null=True)
    telefono_contacto = models.CharField('Teléfono contacto ventas', max_length=50, blank=True, null=True)

    # Datos bancarios
    nro_cuenta = models.CharField('Nro de cuenta bancaria', max_length=100, blank=True, null=True)
    cbu = models.CharField('CBU', max_length=100, blank=True, null=True)

    proveedor_pago = models.CharField('Proveedor de pagos', max_length=2, choices=settings.PROVEEDORES_PAGO, default='MP')

    # PayPal
    cuenta_paypal = models.EmailField('Cuenta Paypal', blank=True, default=None, null=True)
    # MercadoPago
    mp_client_id = models.CharField('Mercado Pago Client Id', max_length=255, blank=True, null=True)
    mp_client_secret = models.CharField('Mercado Pago Client Secret', max_length=255, blank=True, null=True)
    # PayU
    pu_api_key = models.CharField('PayU Api Key', max_length=255, blank=True, null=True)
    pu_api_login = models.CharField('PayU Api Login', max_length=255, blank=True, null=True)
    pu_account_id = models.IntegerField('PayU Account Id', blank=True, null=True)
    pu_merchand_id = models.IntegerField('PayU Merchand Id', blank=True, null=True)


    # Otros Datos
    ind_marca_activa = models.BooleanField('Marca Activa', default=True)
    valor_promocion_envio = models.DecimalField('Importe mínimo de promoción del envío', max_digits=15, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    contrato_firmado = models.FileField('Contrato firmado', upload_to='images/contratos_firmados', blank=True, default=None, null=True)
    terminos = models.BooleanField(u"Acepto los términos y condiciones de uso", default=False)

    def get_marca_seguida(marca_obj, serializer):
        request = serializer.context.get('request')
        user = getattr(request, 'user', None)

        if user.username:
            try:
                user_comprador = auth_api.models.UserComprador.objects.get(username=user.username)
            except:
                return False
                #raise serializers.ValidationError("No se encuentra el Usuario Comprador")
            else:
                if MarcaSeguida.objects.filter(usuario=user_comprador, marca=marca_obj).exists():
                    return True
                else:
                    return False
        else:
            #raise serializers.ValidationError("Usuario Comprador inválido o inexistente")
            return False

    def get_productos_oferta_por_marca(marca_obj):
        fecha_hoy = datetime.date.today()
        qs_productos_oferta = Producto.objects.filter(marca=marca_obj, fecha_descuento_desde__lte=fecha_hoy,
                              fecha_descuento_hasta__gte=fecha_hoy).order_by('-date_created')
        return qs_productos_oferta

    def get_deposito_default(self):
        try:
            deposito_default = Deposito.objects.get(marca=self, ind_deposito_default=True)
        except:
            deposito_default = None

        return deposito_default

    def __str__(self):
        return u'%s' % (self.nombre)


class Deposito(models.Model):
    # Datos y Domicilio del depósito
    nombre_deposito = models.CharField('Nombre del depósito', max_length=50)
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="deposito_marca")
    ind_deposito_default = models.BooleanField('Indicador depósito de default', default=False)
    contacto_deposito = models.CharField('Contacto en el depósito',
                                            help_text="Nombre y apellido del contacto",
                                            max_length=100, blank=True, null=True)
    telefono_contacto = models.CharField('Teléfono del Contacto del depósito',
                                            help_text="Numero telefónico del contacto",
                                            max_length=30, blank=True, null=True)
    calle = models.CharField('Calle', help_text="Nombre de la calle",
                                            max_length=50)
    numero = models.CharField('Número', max_length=10)
    piso = models.CharField('Piso', max_length=6, blank=True, null=True)
    departamento = models.CharField('Departamento', max_length=4, blank=True, null=True)
    provincia = models.CharField('Provincia', max_length=25)
    localidad = models.CharField('Localidad', max_length=50)
    cod_postal = models.ForeignKey('configuraciones.CodigoPostal', on_delete=models.PROTECT, related_name="cod_postal_deposito")

    class Meta:
        verbose_name = "Depósito"
        verbose_name_plural = "Depósitos"

    def __str__(self):
        return smart_text(self.nombre_deposito) + ' - ' + smart_text(self.calle) + ' - ' + \
            smart_text(self.numero) + ' - ' + smart_text(self.localidad)


class Categoria(models.Model):
    nombre = models.CharField('Nombre de Categoría', max_length=30, unique=True)
    imagen = models.ImageField('Imagen de la Categoría', upload_to='images/categorias', blank=True, null=True)
    categoria_padre = models.ForeignKey('self', blank=True, null=True, related_name='categoria_hijos')
    #tabla_talles = models.ImageField('Tabla de Talles', upload_to='images/tabla_talles', blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        if not self.categoria_padre:
            return u'%s' % (self.nombre)
        else:
            return u'%s' % (self.categoria_padre.__str__())+' --> '+self.nombre

    def get_subcategorias(self):
        # Esta función obtiene una lista de sus subcategorias. Se incluye la categoria actual
        lista_categorias = [self]
        qs_subcategorias = Categoria.objects.filter(categoria_padre=self)
        for subcategoria in qs_subcategorias:
            lista_subcategorias = subcategoria.get_subcategorias()
            for each_element in lista_subcategorias:
                lista_categorias.append(each_element)
        return lista_categorias

class Local(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="local_marca")
    nombre_local = models.CharField('Nombre del Local', max_length=255)
    direccion = models.CharField('Dirección', max_length=255)
    ciudad = models.CharField('Ciudad', max_length=50)
    telefono = models.CharField('Teléfono', max_length=30)
    cant_calificaciones = models.IntegerField('Cantidad de calificaciones', default=0)
    suma_calificaciones = models.IntegerField('Suma de calificaciones', default=0)
    max_dias_retiro = models.IntegerField('Cantidad máxima de días de retiro', default=7)
    email = models.EmailField('Mail de contacto', blank=True, default=None, null=True)
    horario = models.CharField('Horarios', max_length=255)
    latitud = models.FloatField('Latitud', blank=True, null=True)
    longitud = models.FloatField('Longitud', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Local"
        verbose_name_plural = "Locales"

    def __str__(self):
        return u'%s' % (self.nombre_local)

class FotoLocal(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    foto_local = models.ImageField('Foto del Local', upload_to='images/fotos_locales')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto del Local"
        verbose_name_plural = "Fotos del Local"

    def __str__(self):
        return u'%s' % (self.foto_local)

class Coleccion(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="coleccion_marca")
    nombre_coleccion = models.CharField('Nombre de la Colección', max_length=255)
    descripcion = models.CharField('Descripción', max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Colección"
        verbose_name_plural = "Colecciones"

    def __str__(self):
        return u'%s' % (self.nombre_coleccion)

class FotoColeccion(models.Model):
    coleccion = models.ForeignKey(Coleccion, on_delete=models.CASCADE)
    foto_coleccion = models.FileField('Imagen de la Colección', upload_to='images/media_colecciones')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imagen de la Colección"
        verbose_name_plural = "Imágenes de la Colección"

    def __str__(self):
        return u'%s' % (self.foto_coleccion)

class Novedad(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="novedad_marca")
    titulo_novedad = models.CharField('Título', max_length=255)
    descripcion = models.CharField('Descripción', max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Novedad"
        verbose_name_plural = "Novedades"

    def __str__(self):
        return u'%s' % (self.titulo_novedad)

class FotoNovedad(models.Model):
    novedad = models.ForeignKey(Novedad, on_delete=models.CASCADE, related_name="foto_rel_novedad")
    foto_novedad = models.ImageField('Foto de la Novedad', upload_to='images/fotos_novedades')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imagen de la Novedad"
        verbose_name_plural = "Imágenes de la Novedad"

    def __str__(self):
        return u'%s' % (self.foto_novedad)
        

class Producto(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="producto_marca")
    nombre_producto = models.CharField('Nombre del Producto', max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    coleccion = models.ForeignKey(Coleccion, on_delete=models.PROTECT, blank=True, default=None, null=True)
    precio = models.DecimalField('Precio', max_digits=15, decimal_places=2, validators=[validate_positive], default=1)
    descripcion = models.CharField('Descripción', max_length=255)
    cod_producto = models.CharField('Código de Producto', max_length=20, blank=True, null=True)
    color = models.CharField('Color', max_length=50, blank=True, null=True)
    foto_principal = ContentTypeRestrictedImageField('Foto Principal', upload_to='images/fotos_productos', default='images/fotos_productos/Sin_imagen_disponible.jpg')
    foto_principal_optim = models.ImageField('Foto Principal Optimizada', upload_to='images/fotos_productos/optim', null=True, blank=True, editable=False)
    foto_principal_thumb = models.ImageField('Foto Principal Thumbnail', upload_to='images/fotos_productos/thumb', null=True, blank=True, editable=False)
    #ind_oferta = models.BooleanField('Producto en Oferta', default=False)
    #precio_oferta = models.DecimalField('Precio de oferta', max_digits=15, decimal_places=2, validators=[validate_non_negative], default=0)
    #fecha_oferta_desde = models.DateField('Fecha de Oferta desde', blank=True, null=True)
    #fecha_oferta_hasta = models.DateField('Fecha de Oferta hasta', blank=True, null=True)
    porc_descuento = models.DecimalField('Porcentaje de descuento', max_digits=4, decimal_places=2, validators=[validate_percentaje], default=0)
    fecha_descuento_desde = models.DateField('Fecha de Descuento desde', blank=True, null=True)
    fecha_descuento_hasta = models.DateField('Fecha de Descuento hasta', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    tipo_prenda = models.CharField('Tipo de prenda', max_length=2, choices=TIPO_PRENDA, default='PS')
    segmento_edad = models.CharField('Segmento de edad', max_length=15, choices=SEGMENTO_EDAD, default='ADULTO')
    segmento_sexo = models.CharField('Segmento de sexo', max_length=15, choices=SEGMENTO_SEXO, default='HOMBRE')
    imagen_talles = models.ImageField('Imagen de Talles', upload_to='images/tabla_talles', blank=True, null=True)
    tags = TaggableManager(verbose_name="Tags", blank=True)


    def get_prod_favorito(producto_obj, serializer):
        request = serializer.context.get('request')
        user = getattr(request, 'user', None)

        if user:
            try:
                user_comprador = auth_api.models.UserComprador.objects.get(username=user.username)
            except:
                return False
                #raise serializers.ValidationError("No se encuentra el Usuario Comprador")
            else:
                if WishList.objects.filter(usuario=user_comprador, producto=producto_obj).exists():
                    return True
                else:
                    return False
        else:
            return False

    def get_precio_actual(producto_obj):
        fecha_descuento_desde = producto_obj.fecha_descuento_desde
        fecha_descuento_hasta = producto_obj.fecha_descuento_hasta

        if fecha_descuento_desde and fecha_descuento_hasta:
            fecha_hoy = datetime.date.today()
            if fecha_descuento_desde <= fecha_hoy and fecha_hoy <= fecha_descuento_hasta:
                precio_actual = producto_obj.precio * (1 - producto_obj.porc_descuento * Decimal('0.01'))
            else:
                precio_actual = producto_obj.precio
        else:
            precio_actual = producto_obj.precio

        return round(precio_actual, 2)

    def ind_oferta(producto_obj):
        fecha_descuento_desde = producto_obj.fecha_descuento_desde
        fecha_descuento_hasta = producto_obj.fecha_descuento_hasta

        if fecha_descuento_desde and fecha_descuento_hasta:
            fecha_hoy = datetime.date.today()
            if fecha_descuento_desde <= fecha_hoy and fecha_hoy <= fecha_descuento_hasta:
                ind_oferta = 1
            else:
                ind_oferta = 0
        else:
            ind_oferta = 0

        return ind_oferta

    def __str__(self):
        return u'%s' % (self.nombre_producto)

    def get_combinaciones(self):
        qs_combina_con = Combinacion.objects.filter(
                producto=self).select_related('combina_con')
        list_combina_con = []
        for combinacion in qs_combina_con:
            list_combina_con.append(combinacion.combina_con)
        return list_combina_con

    def get_stock(self):
        qs_stock = TalleProducto.objects.filter(
                producto=self)
        return qs_stock

    def generate_optim_pictures(self):
        from django.core.files.base import ContentFile
        if not self.foto_principal:
            return
        temp_thumb, filename, file_ext = generate_optim_picture(self.foto_principal)
        # Save image field
        self.foto_principal_optim.save(filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        temp_thumb, filename, file_ext = generate_thumb_picture(self.foto_principal)
        self.foto_principal_thumb.save(filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

    def save(self, *args, **kwargs):
        if not self.id:
            super(Producto, self).save(*args, **kwargs)
            self.generate_optim_pictures()
            super(Producto, self).save(update_fields=['foto_principal_optim', 'foto_principal_thumb']) 
        else:
            this = Producto.objects.get(id=self.id)
            if (this.foto_principal != self.foto_principal) or \
                             not this.foto_principal_optim or not this.foto_principal_thumb:            
                super(Producto, self).save(update_fields=['foto_principal']) 
                self.generate_optim_pictures()
            
            super(Producto, self).save(*args, **kwargs)


class FotoProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="foto_rel_producto")
    foto_producto = ContentTypeRestrictedImageField('Foto del Producto', upload_to='images/fotos_productos', help_text='Formatos válidos: jpg, jpeg, gif, png')
    foto_producto_optim = models.ImageField('Foto de Producto Optimizada', upload_to='images/fotos_productos/optim', null=True, blank=True, editable=False)
    foto_producto_thumb = models.ImageField('Foto de Producto Thumbnail', upload_to='images/fotos_productos/thumb', null=True, blank=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto del Producto"
        verbose_name_plural = "Fotos del Producto"

    def generate_optim_pictures(self):
        from django.core.files.base import ContentFile
        if not self.foto_producto:
            return
        temp_thumb, filename, file_ext = generate_optim_picture(self.foto_producto)
        # Save image field
        self.foto_producto_optim.save(filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        temp_thumb, filename, file_ext = generate_thumb_picture(self.foto_producto)
        self.foto_producto_thumb.save(filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()


    def save(self, *args, **kwargs):
        super(FotoProducto, self).save()
        self.generate_optim_pictures()
        super(FotoProducto, self).save(update_fields=['foto_producto_optim', 'foto_producto_thumb']) 


class Foto360Producto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="foto360_rel_producto")
    #foto360_producto = models.ImageField('Foto 360 del Producto', upload_to='images/fotos_productos')
    descripcion = models.CharField('Descripción', max_length=255, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foto 360 del Producto"
        verbose_name_plural = "Fotos 360 del Producto"

class TomaFoto360(models.Model):
    foto360 = models.ForeignKey(Foto360Producto, on_delete=models.CASCADE, related_name="toma_rel_foto360")
    foto360_imagen = models.ImageField('Toma de Foto 360 del Producto', upload_to='images/fotos360_productos')
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Toma de Foto 360 del Producto"
        verbose_name_plural = "Tomas de Fotos 360 del Producto"  


class ColorProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="color_producto_original")
    otro_color = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="color_producto_otro")

    class Meta:
        verbose_name = "Otro Color"
        verbose_name_plural = "Otros Colores"
        unique_together = ("producto", "otro_color")

    def __str__(self):
        return u'%s' % (self.otro_color.color)

def validate_talle(value):
    if set('-[~!@#$%^&*()_+{}":;\' ]+$').intersection(value):
        raise ValidationError(
            '%(value)s no es un formato admitido. Formatos válidos: cadena de caracteres o número',
            params={'value': value},
        )

class TalleProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="talle_rel_producto")
    talle    = models.CharField('Talle', max_length=30, validators=[validate_talle])
    shop_sku = models.CharField('ShopSku', max_length=30, default=' ', blank=True)
    stock    = models.IntegerField('Stock', validators=[validate_non_negative], default=0, help_text='El stock del producto')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Talle del Producto"
        verbose_name_plural = "Talles del Producto"

    def __str__(self):
        return u'%s' % (self.talle)


class Combinacion(models.Model):
    producto    = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="rel_producto_original")
    combina_con = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="rel_producto_combinado")

    class Meta:
        verbose_name = "Combinación"
        verbose_name_plural = "Combinaciones"
        unique_together = ("producto", "combina_con")


class Post(models.Model):
    marca = models.ForeignKey(Marca, on_delete=models.PROTECT, related_name="post_marca")
    nombre_post = models.CharField('Nombre del Posteo', max_length=255)
    descripcion = models.CharField('Descripción', max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Posteo"
        verbose_name_plural = "Posteos"

    def __str__(self):
        return u'%s' % (self.nombre_post)

class ImagenPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="imagen_post")
    imagen_post = ContentTypeRestrictedFileField('Imagen del Posteo', upload_to='images/media_posteos', help_text='Formatos válidos: jpg, jpeg, gif, png')
    imagen_post_optim = models.ImageField('Imagen del Posteo Optimizada', upload_to='images/media_posteos/optim', null=True, blank=True, editable=False)
    imagen_post_thumb = models.ImageField('Imagen del Posteo Thumbnail', upload_to='images/media_posteos/thumb', null=True, blank=True, editable=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Imagen del Posteo"
        verbose_name_plural = "Imágenes del Posteo"

    def __str__(self):
        return u'%s' % (self.imagen_post)

    def generate_optim_pictures(self, *args, **kwargs):
        from django.core.files.base import ContentFile
        if not self.imagen_post:
            return

        # Chequea si la imagen_post es foto o video - Si es foto genera las versiones optimizadas
        import mimetypes

        file_type = mimetypes.guess_type(self.imagen_post.url)[0]

        flag_is_picture = file_type in settings.PICTURE_TYPES

        if flag_is_picture:
            temp_thumb, filename, file_ext = generate_optim_picture(self.imagen_post)
            # Save image field
            self.imagen_post_optim.save(filename, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()
            temp_thumb, filename, file_ext = generate_thumb_picture(self.imagen_post)
            self.imagen_post_thumb.save(filename, ContentFile(temp_thumb.read()), save=False)
            temp_thumb.close()


    def save(self, *args, **kwargs):
        super(ImagenPost, self).save()
        self.generate_optim_pictures(*args, **kwargs)
        super(ImagenPost, self).save(update_fields=['imagen_post_optim', 'imagen_post_thumb']) 


class VideoLinkPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="video_link_post")
    video_link = EmbedVideoField('Link de Video', max_length=150, help_text='Ingresar Link de Video')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Link de Video"
        verbose_name_plural = "Links de Video"

    def __str__(self):
        return u'%s' % (self.video_link)


class MarcaSeguida(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_marca_seguida")
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="marca_marca_seguida")

    class Meta:
        verbose_name = "Usuario Seguidor de Marca"
        verbose_name_plural = "Usuarios Seguidores de Marca"
        unique_together = ("usuario", "marca")

'''
class ProductoFavorito(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_producto_favorito")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="producto_producto_favorito")

    class Meta:
        verbose_name = "Producto Favorito"
        verbose_name_plural = "Productos Favoritos"
        unique_together = ("usuario", "producto")
'''

class WishList(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_wish_list")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="producto_wish_list")
    talle = models.ForeignKey(TalleProducto, on_delete=models.CASCADE, related_name="talle_wish_list")

    class Meta:
        verbose_name = "Wish List"
        verbose_name_plural = "Wish Lists"
        unique_together = ("usuario", "producto", "talle")


class VistaUserProducto(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_vista_user")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="producto_vista_user")
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vista de Usuario de un Producto"
        verbose_name_plural = "Vistas de Usuarios de Productos"

class LikeColeccion(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_like_coleccion")
    coleccion = models.ForeignKey(Marca, on_delete=models.CASCADE, related_name="coleccion_like_coleccion")

    class Meta:
        verbose_name = "Like de Colección"
        verbose_name_plural = "Likes de Colecciones"
        unique_together = ("usuario", "coleccion")

class LikeFotoColeccion(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_like_fotocoleccion")
    foto_coleccion = models.ForeignKey(FotoColeccion, on_delete=models.CASCADE, related_name="foto_like_fotocoleccion")

    class Meta:
        verbose_name = "Like de Foto de Colección"
        verbose_name_plural = "Likes de Fotos de Colecciones"
        unique_together = ("usuario", "foto_coleccion")

class LikeFotoProducto(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_like_fotoproducto")
    foto_producto = models.ForeignKey(FotoProducto, on_delete=models.CASCADE, related_name="foto_like_fotoproducto")

    class Meta:
        verbose_name = "Like de Foto de Producto"
        verbose_name_plural = "Likes de Fotos de Productos"
        unique_together = ("usuario", "foto_producto")

class LikePost(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_like_post")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_like_post")

    class Meta:
        verbose_name = "Like de Post"
        verbose_name_plural = "Likes de Posts"
        unique_together = ("usuario", "post")


def get_productos_oferta():
    fecha_hoy = datetime.date.today()
    qs_productos_oferta = Producto.objects.filter(fecha_descuento_desde__lte=fecha_hoy,
                                     fecha_descuento_hasta__gte=fecha_hoy).order_by('-date_created')
    return qs_productos_oferta


class AvisoFaltaStock(models.Model):
    usuario = models.ForeignKey('auth_api.UserComprador', on_delete=models.CASCADE, related_name="usuario_falta_stock")
    articulo = models.ForeignKey(TalleProducto, on_delete=models.CASCADE, related_name="aticulo_falta_stock")

    class Meta:
        verbose_name = "Aviso Falta de Stock"
        verbose_name_plural = "Avisos Falta de Stock"
        unique_together = ("usuario", "articulo")

    def __str__(self):
        return u'%s - %s' % (self.usuario.username, self.articulo.talle)


class Notificacion(models.Model):
    usuario = models.ForeignKey(
        'auth_api.UserComprador',
        on_delete=models.CASCADE,
        related_name="usuario_notificacion"
    )
    articulo = models.ForeignKey(
        TalleProducto,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="articulo_notificion"
    )
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    archivar = models.BooleanField(default=False)

    leida_fecha = models.DateTimeField(blank=True, null=True)
    archivar_fecha = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Notificacion"
        verbose_name_plural = "Notificaciones"

    def __str__(self):
        return u'%s - %s' % (
            self.usuario.username, self.articulo.nombre_producto)


class ProcesoBatch(models.Model):
    marca = models.ForeignKey(
        Marca, on_delete=models.PROTECT, related_name="procesobatch_marca")
    tipo = models.CharField(max_length=42, choices=ARCHIVO_BATCH_TIPOS)
    archivo = models.FileField(upload_to=user_directory_path)
    procesado = models.BooleanField(default=False)
    procesado_error = models.BooleanField(default=False)
    procesado_error_tipo = models.CharField(
        blank=True, null=True, max_length=42, choices=ARCHIVO_BATCH_ERROR_TIPOS)
    procesado_fecha = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField('Fecha de carga', auto_now_add=True)
    date_updated = models.DateTimeField('Ultima fecha de actualización', auto_now=True)

    class Meta:
        verbose_name = "Proceso Batch"
        verbose_name_plural = "Procesos Batch"

    def __str__(self):
        return u'%s - %s' % (self.marca.nombre, self.archivo)


class ProcesoBatchError(models.Model):
    proceso_batch = models.ForeignKey(
        ProcesoBatch, on_delete=models.PROTECT,
        related_name="procesobatch_error")
    model_nombre = models.CharField(blank=True, null=True, max_length=255)
    model_id = models.IntegerField(blank=True, null=True)
    linea = models.TextField(blank=True, null=True)
    linea_numero = models.IntegerField(blank=True, null=True)
    error = models.CharField(max_length=255)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ProcesoBatchError"
        verbose_name_plural = "ProcesoBatchErrores"

    def __str__(self):
        return u'%s - %s' % (
            self.proceso_batch.marca.nombre, self.proceso_batch.archivo)
