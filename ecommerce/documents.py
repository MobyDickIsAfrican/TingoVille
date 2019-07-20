

#from django_elasticsearch_dsl import Document, Text
from elasticsearch_dsl import connections, Document, Text
from .models import Shop, Product, ProductImage
connections.create_connection(hosts = ['localhost'], timeout = 100)

class ProductDocument(Document):
    #snowball uses stop words, standard tokenizer
    ProductType = Text(analyzer = 'snowball')
    Name = Text(analyzer = 'snowball')
    Description = Text(analyser = 'snowball')

    class Index:
        name = 'products'
        settings = {'number_of_shards' :3, 'number_of_replicas' : 1}

    def save(self, **kwargs):
        super(ProductDocument).save(self, **kwargs)

class ShopDocument(Document):
    Name = TextField(analyzer = 'snowball')

    class Index:
        name = 'shops'
        settings = {'number_of_shards': 2, 'number_of_replicas' : 1 }
