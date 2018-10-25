from django.dispatch import receiver
from django.db.models.signals import post_save

from mercado_vindu.models import TalleProducto, AvisoFaltaStock, TablaTalles

from utils.pushwoosh_client import pw_notify


@receiver(post_save, sender=TalleProducto)
def notificacion_ingreso_stock(sender, **kwargs):
    avisos = AvisoFaltaStock.objects.filter(articulo=sender)

    if avisos.exists():
        for aviso in avisos:
            Notificacion.objects.create(
                usuario=aviso.usuario,
                articulo=aviso.articulo,
                mensaje=u'Articulo en stock',
            )


@receiver(post_save, sender=TablaTalles)
def notificacion_ingreso_talles(sender, instance, **kwargs):
    msg = 'Nuevo Talles Agregado!!!\nTipo de Prenda: %s\nSexo: %s' % (
        instance.tipo_prenda, instance.segmento_sexo
    )
    pw_notify(msg)
