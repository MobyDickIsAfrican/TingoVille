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
    path('my-cart/productimage/<int:id>/', views.CartItemDelete, name = 'cart-item-delete'),
    path('my-cart/checkout/', views.Checkout, name = 'checkout'),
    path('ajax/', views.AjaxView, name = 'ajax-view'),
    path('cart-ajax/', views.AddToCartAjax, name = 'cart-ajax'),
    path('categories', views.CategoryView, name = 'categories'),
    path('product_category/<int:id>/', views.CategoryProducts, name = 'category-products'),
    path('search/', views.Searching, name ='search'),
    path('ajax_search/', views.AjaxSearch, name = 'ajax-search'),
    path('ajax_accept_order/', views.AjaxAccept, name = 'ajax-accept'),
    path('size-ajax/', views.AjaxSize, name = 'size-ajax'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#for development environment

def javascript_settings():
    js_conf = {'ajax_view': reverse('ajax-view'), 'ajax_cart': reverse('cart-ajax'), 'ajax_search': reverse('ajax-search'), 'ajax_Accept': reverse('ajax-accept'), 'ajax_size': reverse('size-ajax')}
    return js_conf
