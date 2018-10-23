# -*- encoding: utf-8 -*-
from django.db import models
#from mercado_vindu.models import Marca
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Meta:
        verbose_name = "Usuario Administrador"
        verbose_name_plural = "Usuarios Administradores"


class UserMarca(User):
    marca = models.ForeignKey('mercado_vindu.Marca', on_delete=models.PROTECT, blank=True, default=None, null=True)
    foto_avatar = models.ImageField('Avatar', upload_to='images/fotos_avatares', blank=True, null=True)

    class Meta:
        verbose_name = "Usuario Marca"
        verbose_name_plural = "Usuarios Marcas"

class UserComprador(User):
    GENEROS = (
       (u'M', u'Masculino'),
       (u'F', u'Femenino'),
     )
    foto_avatar = models.ImageField('Avatar', upload_to='images/fotos_avatares', blank=True, null=True)
    biografia   = models.TextField('Biografía', max_length=200, blank=True, null=True)
    facebook_id = models.CharField(max_length=64, blank=True, null=True)
    dob = models.CharField('Fecha de nacimiento', max_length=10, blank=True, null=True)  #example: 2016-09-29
    genero = models.CharField('Género', max_length=1, choices=GENEROS, blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True, null=True)
    wishlist_publico = models.BooleanField('WishList público', default=True)
    notif_vindu = models.BooleanField('Recibir notificaciones de Vindu', default=True)
    notif_marcas = models.BooleanField('Recibir notificaciones de marcas seguidas', default=True)


    class Meta:
        verbose_name = "Usuario Comprador"
        verbose_name_plural = "Usuarios Compradores"

    def __str__(self):
        return u'%s' % (self.username)

    def save(self, **kwargs):
        self.is_staff = False
        self.is_superuser = False
        #print ('en save de UserComprador kwargs : ' , kwargs)
        super(UserComprador, self).save(**kwargs)


from allauth.account.signals import user_signed_up, user_logged_in
from django.dispatch import receiver
from vindu.emails_manager import enviar_signup_mail

@receiver(user_signed_up, dispatch_uid="vindu.user_signed_up")
def user_signed_up_(request, user, **kwargs):
    if not user.is_staff and not user.is_superuser:
        enviar_signup_mail(request, user)


class UsuarioSeguido(models.Model):
    usuario = models.ForeignKey('UserComprador', on_delete=models.CASCADE, related_name="usuario_usuario_seguidor")
    usuario_seguido = models.ForeignKey('UserComprador', on_delete=models.CASCADE, related_name="usuario_usuario_seguido")

    class Meta:
        verbose_name = "Usuario Seguido"
        verbose_name_plural = "Usuarios Seguidos"
        unique_together = ("usuario", "usuario_seguido")





