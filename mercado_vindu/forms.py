# -*- encoding: utf-8 -*-
from django import forms
from django.utils.safestring import mark_safe
from mercado_vindu.models import *
from auth_api.models import UserMarca, UserComprador
from django.forms.models import BaseInlineFormSet


CONDICION_IVA = (
    ('RI', 'Responsable Inscripto'),
    ('RN', 'Responsable No Inscripto'),
    ('MO', 'Monotributista'),
    ('EX', 'Exento'),
)

def validate_image_formats(file):
    valid_extensions =  {".jpg", "jpeg", ".png", ".gif"}
    if file:
        if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError("Formato de archivo inválido")

def validate_media_formats(file):
    valid_extensions =  {".jpg", "jpeg", ".png", ".gif", ".mp4"}
    if file:
        if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError("Formato de archivo inválido")

def validate_pdf_format(file):
    valid_extensions =  {".pdf"}
    if file:
        if not any(file.name.lower().endswith(ext) for ext in valid_extensions):
            raise forms.ValidationError("Formato de archivo inválido")


class AdminImageWidget(forms.FileInput):
    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []

        if value and getattr(value, "url", None):
            extensions = {".jpg", "jpeg", ".png", ".gif"}
            file_name=str(value)
            image_url = value.url
            if any(file_name.endswith(ext) for ext in extensions):
                output.append(('<a target="_blank" href="%s">'
                            '<img src="%s" style="height: 200px;" /></a> '
                            % (image_url, image_url)))

        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))

class AdminFileWidget(forms.FileInput):
    def __init__(self, attrs={}):
        super(AdminFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []

        if value and getattr(value, "url", None):
            file_extensions = {".jpg", "jpeg", ".png", ".gif"}
            file_name=str(value)
            image_url = value.url
            if any(file_name.endswith(ext) for ext in file_extensions):
                output.append(('<a target="_blank" href="%s">'
                            '<img src="%s" style="height: 200px;" /></a> '
                            % (image_url, image_url)))
            elif file_name.endswith(".mp4"):
                output.append(('<video width="320" height="240" controls>'
                            '<source src="%s" type="video/mp4">'
                            % (image_url)))

        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))



class MarcaAdminForm(forms.ModelForm):
    logo = forms.ImageField(label='Logo formato banner', max_length=100, required=True,
        help_text='Imagen con proporción ancho:alto = 1:0.2037', widget=AdminImageWidget())
    logo_cuadrado = forms.ImageField(label='Logo formato cuadrado', max_length=100, required=True,
        help_text='Logo con alto igual a ancho', widget=AdminImageWidget())
    razon_social     = forms.CharField(label='Razón Social', required=True, max_length=100)
    mail_contacto    = forms.EmailField(label='Mail de contacto', required=True)
    responsable_ventas = forms.CharField(label='Nombre responsable de ventas', required=True, max_length=100)
    telefono_contacto = forms.CharField(label='Teléfono responsable de ventas', required=True, max_length=50)
    porcentaje_vindu = forms.DecimalField(label='Porcentaje comisión Vindu', required=True, initial=10) 
    contrato_firmado = forms.FileField(label='Contrato firmado', max_length=100, required=True,
        help_text='Formato válido: pdf ')
    terminos = forms.BooleanField(label='Acepto las bases y condiciones', required=True)

    domicilio_fiscal = forms.CharField(label='Domicilio Fiscal', required=True, max_length=100)
    cuit_nro = forms.CharField(label='Cuit Nro', max_length=50, required=True)
    condicion_iva = forms.ChoiceField(label='Condición ante el IVA', required=True, choices=CONDICION_IVA, initial='RI')
    agente_ret_ib = forms.BooleanField(label='Agente de retención de Ingresos Brutos', required=False)
    agente_ret_gan = forms.BooleanField(label='Agente de retención de Ganancias', required=False)
    agente_ret_iva = forms.BooleanField(label='Agente de retención de IVA', required=False)

    def clean_contrato_firmado(self):
        image_file = self.cleaned_data.get('contrato_firmado')
        validate_pdf_format(image_file)
        return image_file

    def clean(self):
        proveedor_pago = self.cleaned_data.get('proveedor_pago')
        mp_client_id = self.cleaned_data.get('mp_client_id')
        mp_client_secret = self.cleaned_data.get('mp_client_secret')

        pu_api_key = self.cleaned_data.get('pu_api_key')
        pu_api_login = self.cleaned_data.get('pu_api_login')
        pu_account_id = self.cleaned_data.get('pu_account_id')
        pu_merchand_id = self.cleaned_data.get('pu_merchand_id')

        if proveedor_pago == 'MP':
            if not (mp_client_id and mp_client_secret):
                raise forms.ValidationError('Se debe informar las credenciales de MercadoPago')

        elif proveedor_pago == 'PU':
            if not (pu_api_key and pu_api_login and pu_account_id and pu_merchand_id):
                raise forms.ValidationError('Se debe informar las credenciales de PayU')

        return self.cleaned_data

    class Meta:
        model = Marca
        fields = '__all__'

class CategoriaAdminForm(forms.ModelForm):
    imagen = forms.ImageField(label='Imagen de la Categoría', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())

    class Meta:
        model = Categoria
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(CategoriaAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['categoria_padre'].queryset = Categoria.objects.exclude(id=self.instance.id)


    def clean_imagen(self):
        image_file = self.cleaned_data.get('imagen')
        validate_image_formats(image_file)
        return image_file

    def clean(self):
        categoria_padre = self.cleaned_data.get('categoria_padre')
        imagen          = self.cleaned_data.get('imagen')

        if not categoria_padre and not imagen:
            raise forms.ValidationError('En la categoría de mayor nivel es obligatorio cargar la imagen')

        return self.cleaned_data


class FotoColeccionAdminForm(forms.ModelForm):
    foto_coleccion = forms.FileField(label='Imagen de la Colección', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png, mp4', widget=AdminFileWidget())

    class Meta:
        model = FotoColeccion
        fields = '__all__'

    def clean_foto_coleccion(self):
        image_file = self.cleaned_data.get('foto_coleccion')
        validate_media_formats(image_file)
        return image_file


class ColeccionAdminForm(forms.ModelForm):
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)

    class Meta:
        model = Coleccion
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ColeccionAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True


class FotoLocalAdminForm(forms.ModelForm):
    foto_local = forms.ImageField(label='Foto del Local', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())

    class Meta:
        model = FotoLocal
        fields = '__all__'

    def clean_foto_local(self):
        image_file = self.cleaned_data.get('foto_local')
        validate_image_formats(image_file)
        return image_file


class LocalAdminForm(forms.ModelForm):
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)

    class Meta:
        model = Local
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(LocalAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True


class ColorProductoAdminForm(forms.ModelForm):

    class Meta:
        model = ColorProducto
        fields = '__all__'

class TalleProductoAdminForm(forms.ModelForm):

    class Meta:
        model = TalleProducto
        fields = '__all__'


class CombinacionAdminForm(forms.ModelForm):

    class Meta:
        model = Combinacion
        fields = '__all__'    


class FotoProductoAdminForm(forms.ModelForm):
    foto_producto = forms.ImageField(label='Foto del Producto', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())

    class Meta:
        model = FotoProducto
        fields = '__all__'

    def clean_foto_producto(self):
        image_file = self.cleaned_data.get('foto_producto')
        validate_image_formats(image_file)
        return image_file

class TomaFoto360AdminForm(forms.ModelForm):
    foto360_imagen = forms.ImageField(label='Toma de Foto 360 del Producto', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())

    def clean_foto360_imagen(self):
        image_file = self.cleaned_data.get('foto360_imagen')
        validate_image_formats(image_file)
        return image_file


class Foto360ProductoAdminForm(forms.ModelForm):

    class Meta:
        model = Foto360Producto
        fields = '__all__'


class ProductoAdminForm(forms.ModelForm):
    id    = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)
    foto_principal = forms.ImageField(label='Foto Principal', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())
    imagen_talles = forms.ImageField(label='Imagen de Talles', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminImageWidget())

    class Meta:
        model = Producto
        exclude = ['foto_principal_optim', 'foto_principal_thumb']

    def __init__(self, *args, **kwargs):
        super(ProductoAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque la marca está en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True
            # Filtro también las colecciones pertenecientes a la marca
            self.fields['coleccion'].queryset = Coleccion.objects.filter(marca=user.marca)
            # Un usuario de marca no puede cambiar la imagen_talles
            self.fields['imagen_talles'].widget.attrs['disabled'] = 'disabled'
            self.fields['imagen_talles'].help_text = ''

    def clean_foto_principal(self):
        image_file = self.cleaned_data.get('foto_principal')
        validate_image_formats(image_file)
        return image_file

    def clean_imagen_talles(self):
        image_file = self.cleaned_data.get('imagen_talles')
        validate_image_formats(image_file)
        return image_file

    def clean_porc_descuento(self):
        porc_descuento = self.cleaned_data.get('porc_descuento')
        if porc_descuento:
            if porc_descuento < 0 or porc_descuento > 100:
                raise ValidationError(
                    _('El porcentaje de descuento debe ser un valor entre 0 y 100')
                )
        return porc_descuento


    def clean(self):
        porc_descuento = self.cleaned_data.get('porc_descuento')
        #print('porc_descuento: ', porc_descuento)
        fecha_descuento_desde = self.cleaned_data.get('fecha_descuento_desde')
        fecha_descuento_hasta  = self.cleaned_data.get('fecha_descuento_hasta')

        if porc_descuento:

            if porc_descuento > 0 and (not fecha_descuento_desde or not fecha_descuento_hasta):
                raise forms.ValidationError('Se debe informar las fechas de descuento desde y hasta')

            if porc_descuento > 0 and (fecha_descuento_desde > fecha_descuento_hasta):
                raise forms.ValidationError('La fecha de descuento DESDE debe ser menor que la fecha HASTA')

        return self.cleaned_data

class FotoNovedadAdminForm(forms.ModelForm):
    foto_novedad = forms.FileField(label='Imagen de la Novedad', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png, mp4', widget=AdminFileWidget())

    def clean_foto_novedad(self):
        image_file = self.cleaned_data.get('foto_novedad')
        validate_media_formats(image_file)
        return image_file


    class Meta:
        model = FotoNovedad
        fields = '__all__'


class NovedadAdminForm(forms.ModelForm):
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)

    class Meta:
        model = Novedad
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(NovedadAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True


class ImagenPostAdminForm(forms.ModelForm):
    imagen_post = forms.FileField(label='Imagen del Posteo', max_length=100, required=False,
        help_text='Formatos válidos: jpg, jpeg, gif, png', widget=AdminFileWidget())

    class Meta:
        model = ImagenPost
        fields = '__all__'

    def clean_imagen_post(self):
        image_file = self.cleaned_data.get('imagen_post')
        # Se eliminan en la primer etapa los videos de Posts, sólo van fotos
        #validate_media_formats(image_file)
        validate_image_formats(image_file)
        return image_file

class PostAdminForm(forms.ModelForm):
    marca = forms.ModelChoiceField(label="Marca", required=True, queryset=Marca.objects.all(), empty_label = None)

    class Meta:
        model = Post
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PostAdminForm, self).__init__(*args, **kwargs)
        user_request = self.request.user

        if not user_request.is_superuser:
            # Esto lo tengo que hacer porque extrañamente la marca no viene en el UserMarca
            user = UserMarca.objects.get(username=user_request.username)
            self.fields['marca'].queryset = Marca.objects.filter(pk=user.marca.id)
            #print ('queryset marca en form:', self.fields['marca'].queryset)
            self.fields['marca'].required = True

class UsuarioSeguidorMarcaAdminForm(forms.ModelForm):

    class Meta:
        model = MarcaSeguida
        fields = '__all__'

class DepositoAdminForm(forms.ModelForm):
    contacto_deposito = forms.CharField(label='Contacto en el depósito',
                                        help_text="Nombre y apellido del contacto",
                                        max_length=100, required=True)
    telefono_contacto = forms.CharField(label='Teléfono del Contacto del depósito',
                                        help_text="Numero telefónico del contacto",
                                        max_length=30, required=True)                                    

    class Meta:
        model = Deposito
        fields = '__all__'

class DepositoAdminFormset(BaseInlineFormSet):

    def clean(self):
        """ Se debe cargar al menos un depósito y uno y sólo uno puede ser de default """
        super(DepositoAdminFormset, self).clean()
        for error in self.errors:
            if error:
                return
        completed = 0
        for cleaned_data in self.cleaned_data:
            # form has data and we aren't deleting it.
            if cleaned_data and not cleaned_data.get('DELETE', False):
                completed += 1


        if completed < 1:
            raise forms.ValidationError('Se debe ingresar al menos un depósito')

        cant_despositos_default = 0
        for form in self.forms:
            try:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    if form.cleaned_data['ind_deposito_default']:
                        cant_despositos_default += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass

        if cant_despositos_default > 1:
            raise forms.ValidationError('Debe haber un solo depósito de default')

        if cant_despositos_default == 0: 
            raise forms.ValidationError('Debe haber un depósito de default')
