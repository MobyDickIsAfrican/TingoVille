default_app_config = 'ecommerce.apps.EcommerceConfig'

from .celery import app as celery_app
__all__ = ['celery_app']
