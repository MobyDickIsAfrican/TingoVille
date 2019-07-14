from django.db import models
from django.conf import settings
from . import views
from django.urls import path
from django.conf.urls.static import static
from django.urls import reverse

urlpatterns = [
    path('', views.Home, name ='home'),
    path('my-shop/', views.MyShop, name ='my-shop'),
    path('product/<int:id>/', views.ProductPage, name= 'product-page'),
    path('my-cart/', views.Cart, name = 'my-cart'),
    path('my-cart/product/<int:id>/', views.CartItemDelete, name = 'cart-item-delete'),
    path('my-cart/checkout/', views.Checkout, name = 'checkout'),
    path('ajax/', views.AjaxView, name = 'ajax-view'),
    path('categories', views.CategoryView, name = 'categories'),
    path('product_category/<int:id>/', views.CategoryProducts, name = 'category-products'),
    #path('categories/', views.CategoriesPage, name ='categories-page')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def javascript_settings():
    js_conf = {'ajax_view': reverse('ajax-view'), }
    return js_conf
