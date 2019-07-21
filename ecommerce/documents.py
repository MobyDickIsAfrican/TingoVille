from elasticsearch_dsl import connections, Document, Text
from .models import Shop, Product, ProductImage
from django.db.models.signals import post_save
from django.dispatch import receiver
import ecommerce.signals.handlers

connections.create_connection(hosts = ['localhost'], timeout = 100)

class ProductDocument(Document):
    #snowball uses stop words, standard tokenizer
    ProductType = Text(analyzer = 'english')
    Name = Text(analyzer = 'english')
    Description = Text(analyser = 'english')

    class Index:
        name = 'products'
        settings = {'number_of_shards' :3, 'number_of_replicas' : 1}

    def save(self, **kwargs):
        super(ProductDocument).save(self, **kwargs)


class ShopDocument(Document):
    Name = Text(analyzer = 'snowball')

    class Index:
        name = 'shops'
        settings = {'number_of_shards': 2, 'number_of_replicas' : 1 }
    def save(self, **kwargs):
        super(ShopDocument).save(self, **kwargs)

class CategoryDocument(Document):
    Name = Text(analyzer = 'english')

    class Index:
        name = 'categories'
        settings = {'number_of_shards': 1, 'number_of_replicas': 1}

    def save(self, **kwargs):
        super(CategoryDocument).save(self, **kwargs)

ShopDocument.init()
CategoryDocument.init()

import ecommerce.signals.handlers
