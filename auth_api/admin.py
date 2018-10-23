from django.contrib import admin
from auth_api.models import User, UserMarca, UserComprador
from mercado_vindu.models import Marca
from auth_api.forms import UserAdminForm, UserMarcaAdminForm 
from django.contrib.auth.models import Group

class UserAdminAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('username', 'password', 'first_name', 'last_name', 'email', )
    list_display_links = ('username', 'email')

    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'first_name', 'last_name', 'email', )
        }),
        ('Permisos', {
             'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions',)
        }),
    )

    def get_queryset(self, request):
        qs = super(UserAdminAdmin, self).get_queryset(request)
        qs_superusuarios = qs.filter(is_superuser=True)
        return qs_superusuarios 


class UserMarcaAdmin(admin.ModelAdmin):
    form = UserMarcaAdminForm
    list_display = ('marca', 'username', 'foto_avatar', 'first_name', 'last_name', 'email', )
    list_display_links = ('username', 'email')
    ordering = ('marca', 'username',)

    fieldsets = (
        (None, {
            'fields': ('username', 'foto_avatar', 'password', 'first_name', 'last_name', 'email', 'marca' )
        }),
        ('Permisos', {
             'fields': ('is_staff', )
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserMarcaAdmin, self).get_form(request, obj=obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super(UserMarcaAdmin, self).get_queryset(request)
        qs_usuarios_marca = qs.filter(is_superuser=False)
        if not request.user.is_superuser:
           # Si es un UserMarca se filtran los usuarios de la marca
           user = UserMarca.objects.get(username=request.user.username)
           qs_usuarios_marca = qs_usuarios_marca.filter(marca=user.marca)
        return qs_usuarios_marca

    def save_model(self, request, obj_user_marca, form, change):
        obj_user_marca.save()
        # Si no está en el grupo usuario_marca se lo agrega
        if not obj_user_marca.groups.filter(name='usuario_marca').exists():
            group = Group.objects.get(name='usuario_marca')
            obj_user_marca.groups.add(group)


class UserCompradorAdmin(admin.ModelAdmin):
    list_display = ('username', 'foto_avatar', 'first_name', 'last_name', 'email', )
    list_display_links = ('username', 'email')


    fieldsets = (
        (None, {
            'fields': ('username', 'foto_avatar', 'biografia', 'password', 'first_name', 'last_name', 'email', 'facebook_id',
             'dob', 'genero', 'wishlist_publico', 'notif_vindu', 'notif_marcas')

        }),
    )

admin.site.register(User, UserAdminAdmin)
admin.site.register(UserMarca, UserMarcaAdmin)
admin.site.register(UserComprador, UserCompradorAdmin)



