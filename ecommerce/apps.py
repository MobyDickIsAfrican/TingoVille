from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    name = 'ecommerce'
    verbose_name = "ecommerce"

    def ready(self):
        import ecommerce.signals.handlers
