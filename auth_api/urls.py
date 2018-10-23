from django.conf.urls import url, include

#from .api import FacebookLoginMio
from .views import RegisterView, LoginView, LogoutView, FacebookLogin, \
                   PasswordResetView, PasswordChangeView, UserDetailsView, UsuarioSeguidoViewSet, \
                   GetUsuariosSeguidosViewSet
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

from rest_framework.routers import DefaultRouter
#from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie

router = DefaultRouter()
           
urlpatterns = [
    url(r'^login', LoginView.as_view()),
    url(r'^logout', LogoutView.as_view()),
    url(r'^signup', csrf_exempt(RegisterView.as_view()), name='rest_register'),
    url(r'^user_facebook_login', FacebookLogin.as_view(), name='fb_login_custom'),
    #url(r'^buscar-usuarios', BuscarUsuariosViewSet.as_view({'get': 'list'})),
    url(r'^reset-password', csrf_exempt(PasswordResetView.as_view())),
    #url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    #    views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^change-password', PasswordChangeView.as_view()),
    url(r'^get-update-mi-perfil', UserDetailsView.as_view()),
]

router.register(r'^get-usuarios-seguidos', GetUsuariosSeguidosViewSet)
router.register(r'^usuario-seguido', UsuarioSeguidoViewSet)
#router.register(r'^buscar-usuarios/(?P<search_string>\w+)', BuscarUsuariosViewSet.as_view({'get': 'list'}), base_name="User")
#router.register(r'^buscar-usuarios/(?P<search_string>\w+)', BuscarUsuariosViewSet)
#router.register(r'^buscar-usuarios', BuscarUsuariosViewSet)

urlpatterns += router.urls