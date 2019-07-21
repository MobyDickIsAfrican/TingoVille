from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    name = 'ecommerce'

class ProductDocumentConfig(AppConfig):
    name = 'ProductDocument'
    verbose_name = "ProductDocuments"

    def ready(self):
        from .signals import handlers

class ShopDocumentConfig(AppConfig):
    name = 'ShopDocument'
    verbose_name = "ShopDocuments"

    def ready(self):
        from .signals import handlers

class CategoryDocumentConfig(AppConfig):
    name = 'CategoryDocument'
    verbose_name = "CategoryDocuments"

    def ready(self):
        from .signals import handlers
