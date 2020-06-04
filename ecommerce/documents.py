from elasticsearch_dsl import connections
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Product, ProductCategory, Shop
import certifi
from django.conf import settings
http_auth = settings.HTTP_AUTH
host = settings.HOST

#This script is to add database models to elasticsearch cluster

connections.create_connection(hosts = host, http_auth = http_auth, use_ssl=True, ca_certs=certifi.where())

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


