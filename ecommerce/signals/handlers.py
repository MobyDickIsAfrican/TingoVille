from django.db.models.signals import post_save
from django.dispatch import receiver
from ecommerce.models import Product, Shop, ProductCategory
from ecommerce.documents import ProductDocument

@receiver(post_Save, sender = Product)
def UpdateProductDocument(sender, instance, created, **kwargs):
    if created:
        doc = ProductDocument(ProductType = instance.ProductType, Name = instance.Name, Description = instance.Description, meta = {'id' = instance.id})
        doc.save()
