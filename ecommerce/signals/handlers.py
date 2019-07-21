from django.db.models.signals import post_save
from django.dispatch import receiver
from ecommerce.models import Product, Shop, ProductCategory
#from ecommerce.documents import ProductDocument, ShopDocument, CategoryDocument

@receiver(post_save, sender = Product)
def UpdateProductDocument(sender, instance, created, **kwargs):
    if created:
        doc = ProductDocument(ProductType = instance.ProductType, Name = instance.Name, Description = instance.Description, meta = {'id' : instance.id})
        doc.save()

@receiver(post_save, sender = Shop)
def UpdateShopDocument(sender, instance, created, **kwargs):
    if created:
        doc = ShopDocument(Name = instance.Shop_Name, meta = {'id': instance.id})
        doc.save()

@receiver(post_save, sender = ProductCategory)
def UpdateCategoryDocument(sender, instance, created, **kwargs):
    if created:
        doc = CategoryDocument(Name = instance.CategoryName, meta = {'id': instance.id})
        doc.save()
