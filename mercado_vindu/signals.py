from django.dispatch import receiver
from django.db.models.signals import post_save

from mercado_vindu.models import TalleProducto, AvisoFaltaStock


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
