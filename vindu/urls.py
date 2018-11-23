"""vindu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import logout
from django.views.generic.base import RedirectView
from mercado_vindu.views import *
from django.contrib.auth import views

admin.site.site_header = 'Administración de Vindu'
admin.site.site_title = 'Administración de Vindu'


def pw_service_worker(request):
    file_path = settings.PROJECT_DIR + '\\static\\push-notifications\\pushwoosh-service-worker.js'
    with open(file_path, 'rb') as data:
        return HttpResponse(data, content_type='application/javascript')


urlpatterns = [
    #url(r'^$', RedirectView.as_view(url='/admin')),
    url(r'^admin/', admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^tinymce/', include('tinymce.urls')),
    #url(r'^mercado-vindu/', include('mercado_vindu.urls')),
    url(r'^', include('mercado_vindu.urls')),
    url(r'carrito/', include('carrito.urls')),
    url(r'auth_api/', include('auth_api.urls')),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^prueba_login_facebook', PruebaLoginFacebook),
    #url(r'^usuarios/', include('django.contrib.auth.urls')),
    url(r'^usuarios/password_reset/$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^usuarios/password_reset/done/$', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^usuarios/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^usuarios/reset/done/$', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),   
    url(r'^usuarios/password_reset/$', views.PasswordResetView.as_view(), name='password_reset'), 
    url(r'^usuarios/logout/$', logout, {'next_page': '/'}, name='logout'),
    #url(r'^auth/convert_access_token/?$', ConvertTokenView.as_view(), name="convert_access_token"),
    #url(r'^accounts/', include('allauth.urls')),
    url(r'^get-imagen-ppal-byProductoId/(?P<producto_id>\d+)', get_imagen_ppal_por_producto_id),
    url(r'configuraciones/', include('configuraciones.urls')),
    url(r'pagos/', include('pagos.urls', namespace='pagos')),
    url(r'reportes/', include('reportes.urls', namespace='reportes')),
    url('^pushwoosh-service-worker\.js.*$', pw_service_worker),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
