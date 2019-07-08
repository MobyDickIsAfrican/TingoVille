from django.db import models
from django.conf import settings
from . import views
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home, name ='home'),
    path('shop/', views.MyShop, name ='my-shop'),
    path('product/<int:id>/', views.ProductPage, name= 'product-page'),
    path('my-cart/', views.Cart, name = 'my-cart'),
    path('my-cart/product/<int:id>/', views.CartItemDelete, name = 'cart-item-delete')
    #path('categories/', views.CategoriesPage, name ='categories-page')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
