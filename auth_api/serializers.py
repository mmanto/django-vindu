from .models import User, UserMarca, UserComprador, UsuarioSeguido
from mercado_vindu.models import Marca, MarcaSeguida, WishList, Producto

from rest_framework import serializers, exceptions
from allauth.utils import (email_address_exists, get_username_max_length)
from allauth.account.adapter import get_adapter
from allauth.account import app_settings as allauth_settings
from rest_framework.authtoken.models import Token as TokenModel
from django.utils.translation import ugettext_lazy as _
from allauth.account.utils import setup_user_email
from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from auth_api.forms import CustomPasswordResetForm
from rest_framework.validators import UniqueTogetherValidator

'''
class UserSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.SerializerMethodField()
    foto_avatar  = serializers.SerializerMethodField()

    def get_tipo_usuario(self, obj):
        username_usuario_obj = obj.username
        try:
            user_comprador = UserComprador.objects.get(username=username_usuario_obj)
        except:
            pass
        else:
            return 'Usuario Comprador'

        try:
            user_marca = UserMarca.objects.get(username=username_usuario_obj)
        except:
            raise exceptions.NotFound(detail="Tipo de usuario desconocido")
        else:
            return "Usuario Marca"

    def _get_foto_avatar_or_null(self, foto_obj):
        try:
            url = foto_obj.url
        except:
            return ''
        else:
            request = self.context.get('request')
            photo_url = foto_obj.url
            return request.build_absolute_uri(photo_url)

    def get_foto_avatar(self, obj):
        username_usuario_obj = obj.username
        try:
            user_comprador = UserComprador.objects.get(username=username_usuario_obj)
        except:
            pass
        else:
            return self._get_foto_avatar_or_null(user_comprador.foto_avatar)

        try:
            user_marca = UserMarca.objects.get(username=username_usuario_obj)
        except:
            raise exceptions.NotFound(detail="Tipo de usuario desconocido")
        else:
            return self._get_foto_avatar_or_null(user_marca.foto_avatar)

    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'foto_avatar', 'tipo_usuario')
'''

class UserCompradorSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserComprador
        fields = ('id', 'first_name', 'last_name', 'username', 'genero')

class UserCompradorUsernameSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserComprador
        fields = ('username',)


class UserCompradorUsernameSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserComprador
        fields = ('username',)


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserComprador
        fields = ('id', 'username', 'password', 'email', 'first_name', 'last_name', 'dob', 'genero')

    username = serializers.CharField(
        #max_length=get_username_max_length(),
        #min_length=allauth_settings.USERNAME_MIN_LENGTH,
        max_length=20,
        min_length=6,
        required=True
    )
    #email = serializers.EmailField(required=allauth_settings.EMAIL_REQUIRED)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    dob = serializers.CharField(required=False)
    genero = serializers.CharField(required=True)


    def validate_username(self, username):
        username = get_adapter().clean_username(username)
        return username

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if allauth_settings.UNIQUE_EMAIL:
            if email and email_address_exists(email):
                raise serializers.ValidationError(
                    _("La dirección de mail ya está registrada."))
        return email

    def validate_password(self, password):
        return get_adapter().clean_password(password)

    def validate_dob(self, dob):
        import datetime
        try:
            datetime.datetime.strptime(dob, '%Y-%m-%d')
        except:
            raise serializers.ValidationError(
                _("Fecha inválida. El formato debe ser: AAAA-MM-DD"))

        return dob

    def validate_genero(self, genero):
        if not genero == 'M' and not genero == 'F':
            raise serializers.ValidationError(
                _("Género inválido. El género debe ser 'M' o 'F'"))
        return genero

    def custom_signup(self, request, user):
        pass

    def get_cleaned_data(self):
        return {
            'username': self.validated_data.get('username', ''),
            'password': self.validated_data.get('password', ''),
            'email': self.validated_data.get('email', ''),
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'dob': self.validated_data.get('dob', ''),
            'genero': self.validated_data.get('genero', ''),
        }

    def save(self, request):
        self.cleaned_data = self.get_cleaned_data()
        user = super(RegisterSerializer, self).create(self.cleaned_data)
        password = self.cleaned_data['password']
        user.set_password(password)
        user.save()
        return user


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = TokenModel
        fields = ('key',)


class SocialLoginSerializer(serializers.Serializer):
    access_token = serializers.CharField(required=False, allow_blank=True)
    code = serializers.CharField(required=False, allow_blank=True)

    def _get_request(self):
        request = self.context.get('request')
        if not isinstance(request, HttpRequest):
            request = request._request
        return request

    def get_social_login(self, adapter, app, token, response):
        """
        :param adapter: allauth.socialaccount Adapter subclass.
            Usually OAuthAdapter or Auth2Adapter
        :param app: `allauth.socialaccount.SocialApp` instance
        :param token: `allauth.socialaccount.SocialToken` instance
        :param response: Provider's response for OAuth1. Not used in the
        :returns: A populated instance of the
            `allauth.socialaccount.SocialLoginView` instance
        """
        request = self._get_request()
        social_login = adapter.complete_login(request, app, token, response=response)
        social_login.token = token
        return social_login

    def validate(self, attrs):
        view = self.context.get('view')
        request = self._get_request()

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter_class = getattr(view, 'adapter_class', None)
        if not adapter_class:
            raise serializers.ValidationError(_("Define adapter_class in view"))

        adapter = adapter_class(request)
        app = adapter.get_provider().get_app(request)

        # More info on code vs access_token
        # http://stackoverflow.com/questions/8666316/facebook-oauth-2-0-code-and-token

        # Case 1: We received the access_token
        if attrs.get('access_token'):
            access_token = attrs.get('access_token')

        # Case 2: We received the authorization code
        elif attrs.get('code'):
            self.callback_url = getattr(view, 'callback_url', None)
            self.client_class = getattr(view, 'client_class', None)

            if not self.callback_url:
                raise serializers.ValidationError(
                    _("Define callback_url in view")
                )
            if not self.client_class:
                raise serializers.ValidationError(
                    _("Define client_class in view")
                )

            code = attrs.get('code')

            provider = adapter.get_provider()
            scope = provider.get_scope(request)
            client = self.client_class(
                request,
                app.client_id,
                app.secret,
                adapter.access_token_method,
                adapter.access_token_url,
                self.callback_url,
                scope
            )
            token = client.get_access_token(code)
            access_token = token['access_token']

        else:
            raise serializers.ValidationError(
                _("Incorrect input. access_token or code is required."))

        social_token = adapter.parse_token({'access_token': access_token})
        social_token.app = app

        try:
            login = self.get_social_login(adapter, app, social_token, access_token)
            complete_social_login(request, login)
        except HTTPError:
            raise serializers.ValidationError(_("Incorrect value"))

        if not login.is_existing:
            # We have an account already signed up in a different flow
            # with the same email address: raise an exception.
            # This needs to be handled in the frontend. We can not just
            # link up the accounts due to security constraints
            
            # Cambio en Vindu: si ya existe un usuario registrado en otro flow con el
            # mismo e-mail, se relacionan las dos cuentas
            '''
            if allauth_settings.UNIQUE_EMAIL:
                # Do we have an account already with this email address?
                account_exists = get_user_model().objects.filter(
                    email=login.user.email,
                ).exists()
                if account_exists:
                    raise serializers.ValidationError(
                        _("User is already registered with this e-mail address.")
                    )
            '''
            
            login.lookup()
            login.save(request, connect=True)

        attrs['user'] = login.account.user

        return attrs

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username(self, username, password):
        user = None

        if username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include "username" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def _validate_username_email(self, username, email, password):
        user = None

        if email and password:
            user = authenticate(email=email, password=password)
        elif username and password:
            user = authenticate(username=username, password=password)
        else:
            msg = _('Must include either "username" or "email" and "password".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')

        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                try:
                    username = UserModel.objects.get(email__iexact=email).get_username()
                except UserModel.DoesNotExist:
                    pass

            if username:
                user = self._validate_username_email(username, '', password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    email = serializers.EmailField()

    password_reset_form_class = CustomPasswordResetForm

    def get_email_options(self):
        """Override this method to change default e-mail options"""
        return {}

    def validate_email(self, value):
        # Create PasswordResetForm with the serializer
        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value

    def save(self):
        request = self.context.get('request')
        # Set some values to trigger the send_email method.
        opts = {
            'use_https': request.is_secure(),
            'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }

        opts.update(self.get_email_options())
        self.reset_form.save(**opts)

class PasswordChangeSerializer(serializers.Serializer):

    old_password = serializers.CharField(max_length=128)
    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)

    set_password_form_class = SetPasswordForm

    def __init__(self, *args, **kwargs):
        self.old_password_field_enabled = getattr(
            settings, 'OLD_PASSWORD_FIELD_ENABLED', False
        )
        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False
        )
        super(PasswordChangeSerializer, self).__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Password inválida')
        return value

    def validate(self, attrs):
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )

        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        self.set_password_form.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)

class UserDetailsSerializer(serializers.ModelSerializer):
    """
    User model w/o password
    """
    class Meta:
        model = UserComprador
        fields = ('username', 'email', 'first_name', 'last_name', 'dob', 'genero', 'foto_avatar', 'biografia', \
                  'telefono', 'wishlist_publico', 'notif_vindu', 'notif_marcas')
        read_only_fields = ('email', 'username' )

    def validate_dob(self, dob):
        import datetime
        try:
            datetime.datetime.strptime(dob, '%Y-%m-%d')
        except:
            raise serializers.ValidationError(
                _("Fecha inválida. El formato debe ser: AAAA-MM-DD"))

        return dob

    def validate_telefono(self, telefono):
        if not (telefono and telefono.strip()):
            raise serializers.ValidationError(
                _("Teléfono inválido"))

        return telefono

    def validate_genero(self, genero):
        if not genero == 'M' and not genero == 'F':
            raise serializers.ValidationError(
                _("Género inválido. El género debe ser 'M' o 'F'"))
        return genero

    def validate_foto_avatar(self, foto_avatar):
        valid_extensions =  {".jpg", "jpeg", ".png", ".gif"}   
        if foto_avatar:
            if not any(foto_avatar.name.endswith(ext) for ext in valid_extensions):
                raise serializers.ValidationError(
                "Formato inválido. Las extensiones válidas son: '.jpg', 'jpeg', '.png' o '.gif'")

        return foto_avatar

    def validate_wishlist_publico(self, wishlist_publico):
        if not (wishlist_publico == True or wishlist_publico == False):  
            raise serializers.ValidationError(
                "WishList visible inválido. Los valores posibles son: true o false")

        return wishlist_publico


class GetUsuariosSeguidosSerializer(serializers.ModelSerializer):
    #usuario_id         = serializers.IntegerField(read_only=False, source='usuario_usuario_seguidor')
    usuario = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=UserComprador.objects.all())
    usuario_username_p   = serializers.SerializerMethodField('get_usuario_username')
    usuario_seguido  = UserCompradorSerializer(read_only=False, many=True, source='usuario_usuario_seguido') 
    #usuario_seguido = serializers.PrimaryKeyRelatedField(many=False, read_only=False, queryset=UserComprador.objects.all())

    def get_usuario_username(self, obj):
        return obj.usuario.username

    class Meta:
        model = UsuarioSeguido
        fields = ('usuario', 'usuario_id', 'usuario_username_p', 'usuario_seguido')
        validators = [UniqueTogetherValidator(queryset=UserComprador.objects.all(),
                fields=('usuario', 'usuario_seguido')
            )
        ]

class UsuarioSeguidoSerializer(serializers.ModelSerializer):
    usuario = UserCompradorSerializer(read_only=True, many=False, source='usuario_usuario_seguidor') 
    usuario_seguido = UserCompradorSerializer(read_only=False, many=False, source='usuario_usuario_seguido') 

    class Meta:
        model = UsuarioSeguido
        fields = ('usuario', 'usuario_seguido')
        validators = [UniqueTogetherValidator(queryset=UserComprador.objects.all(),
                fields=('usuario_seguido', 'usuario_seguido')
            )
        ]

    def validate_usuario(self, usuario):
        if not UserComprador.objects.filter(pk=usuario.pk).exists():
            raise serializers.ValidationError("El usuario no existe")
        return username   

    def validate_usuario_seguido(self, usuario_seguido):
        if not UserComprador.objects.filter(pk=usuario_seguido.pk).exists():
            raise serializers.ValidationError("El usuario a seguir no existe")
        return usuario_usuario_seguido

    def validate(self, data):
        #print ('en validate, data= ', data)
        for key, value in data.items():
            # checks if value is empty
            #print ('en validate:, key: ', key , ' and value: ', value)
            if not value:
                raise serializers.ValidationError({key: "This field should not be left empty."})

        return data  

    def create(self, validated_data):
        usuario = validated_data['usuario']
        usuario_seguido = validated_data['usuario_seguido']
        try:     
            nuevo_usuario_seguido = UsuarioSeguido.objects.create(usuario=usuario, usuario_seguido=usuario_seguido)
        except:
            raise serializers.ValidationError("No se pudo agregar el usuario seguido")

        return nuevo_usuario_seguido


class UserMarcaSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserMarca
        fields = ('username', 'first_name', 'last_name', 'password',
                'email', 'foto_avatar')
