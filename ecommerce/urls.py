from django.db import models
from django.conf import settings
from . import views
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    path('', views.Home, name ='home'),
    path('my-shop/', views.MyShop, name ='my-shop'),
    path('product/<int:id>/', views.ProductPage, name= 'product-page')
    #path('categories/', views.CategoriesPage, name ='categories-page')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
