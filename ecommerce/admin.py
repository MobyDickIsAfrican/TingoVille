from django.contrib import admin
from .models import Shop
from .models import Product
from .models import ProductCategory
from .models import Inventory
from .models import OrderItem
from .models import ShoppingCartOrder
from django.contrib.gis.admin import OSMGeoAdmin
from .models import ProductImage

admin.site.register(Product)
admin.site.register(Shop)
admin.site.register(ProductCategory)
admin.site.register(Inventory)
admin.site.register(OrderItem)
admin.site.register(ShoppingCartOrder)
admin.site.register(ProductImage)
