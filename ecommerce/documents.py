from elasticsearch_dsl import connections
from django.db.models.signals import post_save
from django.dispatch import receiver
#from .models import Product, Shop, ProductCategory
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Product, ProductCategory, Shop

connections.create_connection(hosts = ['localhost'], timeout = 10000)

@registry.register_document
class ProductDocument(Document):
    class Index:
        name = 'products'
        settings = {'number_of_shards' :1, 'number_of_replicas' : 1}

    class Django:
        model = Product
        fields = ['ProductType', 'Name', 'Description']

@registry.register_document
class ShopDocument(Document):
    class Index:
        name = 'shops'
        settings = {'number_of_shards': 2, 'number_of_replicas' : 1 }
    class Django:
        model = Shop
        fields = ['Shop_Name']

@registry.register_document
class CategoryDocument(Document):
    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 1}
    class Django:
        model = ProductCategory
        fields = ['CategoryName']

'''
@index.document
class ProductDocument(Document):
    #snowball uses stop words, standard tokenizer
    ProductType = Text()
    Name = Text()
    Description = Text()

    class Index:
        name = 'products'
        settings = {'number_of_shards' :1, 'number_of_replicas' : 1}

    def save(self, **kwargs):
        super(ProductDocument, self).save(self, **kwargs)

@shop_index.document
class ShopDocument(Document):
    Name = Text(analyzer = 'snowball')

    class Index:
        name = 'shops'
        settings = {'number_of_shards': 2, 'number_of_replicas' : 1 }
    def save(self, **kwargs):
        super(ShopDocument, self).save(self, **kwargs)

class CategoryDocument(Document):
    Name = Text(analyzer = 'english')

    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 1}

    def save(self, **kwargs):
        super(CategoryDocument, self).save(self, **kwargs)

ShopDocument.init()
s = ShopDocument(Name = 'Zando', meta = {'id': 150})
s.save()
'''
