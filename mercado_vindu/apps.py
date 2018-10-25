from django.apps import AppConfig


class MercadoVinduConfig(AppConfig):
    name = 'mercado_vindu'
    verbose_name = 'Mercado Vindu'

    def ready(self):
        import mercado_vindu.signals
