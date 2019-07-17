from django_elasticsearch_dsl import DocType, Index, fields
from .models import Shop, Product, ProductImages

product = Index('products')
product.settings(number_of_shards = 1, number_of_replicas = 0)

@product.doc_type
class ProductDocument(DocType):
    shop = fields.Objectfield(properties ={'Shop_Name': fields.TextField})
    productimages = fields.NestedFields(properties = {'name': fields.TextField})
    related_models = [Shop, ProductImages]

    class Meta:
        model = Product
        fields = ['Name', 'ProductType', 'Price', 'Description']
