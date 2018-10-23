# -*- encoding: utf-8 -*-
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth import login, logout

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated)
from rest_framework.generics import CreateAPIView, ListAPIView, GenericAPIView, RetrieveUpdateAPIView
from rest_framework.exceptions import NotFound
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status

from allauth.account.adapter import get_adapter
from allauth.account.views import ConfirmEmailView
from allauth.account.utils import complete_signup
from allauth.account import app_settings as allauth_settings
from allauth.socialaccount import signals
from allauth.socialaccount.adapter import get_adapter as get_social_adapter
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from django.core.exceptions import ObjectDoesNotExist
from rest_framework_social_oauth2.views import ConvertTokenView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator


from .serializers import RegisterSerializer, TokenSerializer, SocialLoginSerializer, LoginSerializer, \
                         PasswordResetSerializer, PasswordChangeSerializer, UserDetailsSerializer, \
                         UsuarioSeguidoSerializer, UserCompradorSerializer, GetUsuariosSeguidosSerializer
                
from rest_framework.authtoken.models import Token as TokenModel
from .models import User, UserComprador, UsuarioSeguido
from auth_api.serializers import UserCompradorSerializer
#from django.views.decorators.csrf import csrf_protect


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters(
        'password', 'old_password', 'new_password1', 'new_password2'
    )
)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    token_model = TokenModel
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def dispatch(self, *args, **kwargs):
        return super(RegisterView, self).dispatch(*args, **kwargs)

    def get_response_data(self, user):
        #if allauth_settings.EMAIL_VERIFICATION == \
        #        allauth_settings.EmailVerificationMethod.MANDATORY:
        #    return {"detail": _("Verification e-mail sent.")}

        return TokenSerializer(user.auth_token).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(self.get_response_data(user),
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def create_token(user):
        token, _ = TokenModel.objects.get_or_create(user=user)
        return token

    #@method_decorator(csrf_protect)
    def perform_create(self, serializer):
        user = serializer.save(self.request)
        token, _ = TokenModel.objects.get_or_create(user=user)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user

class LoginView(GenericAPIView):
    """
    Check the credentials and return the REST Token
    if the credentials are valid and authenticated.
    Calls Django Auth login method to register User ID
    in Django session framework
    Accept the following POST parameters: username, password
    Return the REST Framework Token Object's key.
    """
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    token_model = TokenModel

    @sensitive_post_parameters_m
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def get_response_serializer(self):
        if getattr(settings, 'REST_USE_JWT', False):
            response_serializer = JWTSerializer
        else:
            response_serializer = TokenSerializer
        return response_serializer

    def create_token(self, token_model, user, serializer):
        token, _ = token_model.objects.get_or_create(user=user)
        return token

    def login(self):
        self.user = self.serializer.validated_data['user']

        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = self.create_token(self.token_model, self.user,
                                      self.serializer)

    def get_response(self):
        serializer_class = self.get_response_serializer()

        if getattr(settings, 'REST_USE_JWT', False):
            data = {
                'user': self.user,
                'token': self.token
            }
            serializer = serializer_class(instance=data,
                                          context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token,
                                          context={'request': self.request})

        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)

        self.login()
        return self.get_response()

class LogoutView(APIView):

    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.
    Accepts/Returns nothing.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            request.user.auth_token.delete()
        except (AttributeError, ObjectDoesNotExist):
            pass

        logout(request)

        return Response({"success": "Successfully logged out."},
                        status=status.HTTP_200_OK)


class SocialLoginView(LoginView):
    """
    class used for social authentications
    example usage for facebook with access_token
    -------------
    from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
    class FacebookLogin(SocialLoginView):
        adapter_class = FacebookOAuth2Adapter
    -------------
    example usage for facebook with code
    -------------
    from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    class FacebookLogin(SocialLoginView):
        adapter_class = FacebookOAuth2Adapter
        client_class = OAuth2Client
        callback_url = 'localhost:8000'
    -------------
    """
    serializer_class = SocialLoginSerializer

    def process_login(self):
        get_adapter(self.request).login(self.request, self.user)


class FacebookLogin(APIView):
    permission_classes = (AllowAny,)
    
    def post(self, request):
        #print ('request: ', request)
        access_token=request.data.get("access_token")
        #print ('access_token: ', access_token)

        if access_token is None:
            return Response({
                'status': 'No autorizado',
                'message': 'Access Token incorrecto o inexistente'
            }, status=status.HTTP_401_UNAUTHORIZED)

        else:
            from oauth2_provider.models import Application
            app_oauth2 = Application.objects.get(name='facebook')
            dict_request = { 'grant_type': 'convert_token', 
                             'client_id' : app_oauth2.client_id,
                             'client_secret' : app_oauth2.client_secret,
                             'backend': 'facebook',
                             'token': access_token }

            from django.test import Client
            c = Client()
            response = c.post('/auth/convert-token', dict_request)
            return response

'''
class BuscarUsuariosViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.filter(is_superuser=False)
    serializer_class = UserSerializer
    http_method_names = ['get',]

    def get_queryset(self):
        user = self.request.user
        queryset = super(BuscarUsuariosViewSet, self).get_queryset()
        queryset = queryset.exclude(pk=user.pk)

        #print('self.request: ', self.request.__dict__)
        #search_string = self.kwargs['search_string']
        search_string = self.request.query_params.get('search_string', None)
        #print('search_string: ', search_string , 'longitud: ', len(search_string))

        if not search_string:
            queryset = User.objects.none()
        else:
            queryset = queryset.filter(Q(first_name__icontains=search_string) |
                                    Q(last_name__icontains=search_string)  |
                                    Q(username__icontains=search_string) )                             

        return queryset
'''

class PasswordResetView(GenericAPIView):
    """
    Calls Django Auth PasswordResetForm save method.
    Accepts the following POST parameters: email
    Returns the success/fail message.
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # Create a serializer with request.data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        # Return the success message with OK HTTP status
        return Response(
            {"mensaje": "Se ha enviado un e-mail para el reseteo de la password"},
            status=status.HTTP_200_OK
)

class PasswordChangeView(GenericAPIView):

    """
    Calls Django Auth SetPasswordForm save method.
    Accepts the following POST parameters: new_password1, new_password2
    Returns the success/fail message.
    """

    serializer_class = PasswordChangeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": "Se estableció la nueva password."})


class UserDetailsView(RetrieveUpdateAPIView):
    serializer_class = UserDetailsSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return UserComprador.objects.get(pk=self.request.user.pk)


class GetUsuariosSeguidosViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UsuarioSeguido.objects.all()
    serializer_class = GetUsuariosSeguidosSerializer

    def get_queryset(self):
        """
        Esta vista retorna la lista de usuarios seguidos por el usuario que está logueado
        """
        user = self.request.user
        return self.queryset.filter(usuario=user)

    def list(self, request):
        user = request.user
        usuarios_seguidos = UsuarioSeguido.objects.filter(usuario=user).values('usuario_seguido__username')
        #print ('usuarios_seguidos: ', usuarios_seguidos)
        list_result = [{'username': entry['usuario_seguido__username']} for entry in usuarios_seguidos]  # converts ValuesQuerySet into Python list
        #print ('list_result: ', list_result)
        lista = {'usuario_id': user.id, 'usuario_username': user.username, 'usuarios_seguidos': list_result}
        return Response(lista)


class UsuarioSeguidoViewSet(ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UsuarioSeguido.objects.all()
    serializer_class = UsuarioSeguidoSerializer
    lookup_url_kwarg = "username"

    def get_queryset(self):
        """
        Esta vista retorna los usuarios que sigue el usuario que está logueado
        """
        user = self.request.user
        return self.queryset.filter(usuario__pk=user.pk)

    def post(self, request, format=None, *args, **kwargs):
        #print ('entra a post')
        #print ('request.data: ', request.data)
        username = kwargs.get('username')
        #print ('username: ' , username)
        try:
            usuario_seguido_obj = UserComprador.objects.get(username=username)
        except:
            return Response({"mensaje": "El usuario a seguir no existe"}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        usuario_seguidor = UserComprador.objects.get(username=user.username)

        if user.username == usuario_seguido_obj.username:
            return Response({"mensaje": "Un usuario no puede seguirse a sí mismo"}, status=status.HTTP_400_BAD_REQUEST)

        nuevo_usuario_seguido, created = UsuarioSeguido.objects.get_or_create(usuario=usuario_seguidor, usuario_seguido=usuario_seguido_obj)
        if not created:
            return Response({"mensaje": "Ya se está siguiendo a ese usuario"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"usuario": usuario_seguidor.username, "usuario_seguido":usuario_seguido_obj.username} , status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        username = kwargs.get('username')
        try:
            usuario_seguido_obj = UserComprador.objects.get(username=username)
        except:
            return Response({"mensaje": "El usuario a dejar de seguir no existe"}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        usuario_seguidor = UserComprador.objects.get(username=user.username)

        try:
            usuario_ya_seguido = UsuarioSeguido.objects.get(usuario=usuario_seguidor, usuario_seguido=usuario_seguido_obj)
        except:
            return Response({"mensaje": "No se está siguiendo a ese usuario"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            usuario_ya_seguido.delete()
            return Response({"usuario": usuario_seguidor.username, "usuario_seguido":usuario_seguido_obj.username}, status=status.HTTP_204_NO_CONTENT)





