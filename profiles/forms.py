from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from ecommerce.models import Shop, Product, ProductCategory
import itertools
from django.core.exceptions import ValidationError
from django.forms import formset_factory, modelformset_factory
from ecommerce.models import ProductImage

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    First_Name = forms.CharField()
    Last_Name = forms.CharField()
    contact = forms.CharField()
    Age = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'contact', 'Age', 'First_Name', 'Last_Name','password1', 'password2',]

#allow users to register their shops. this will need to be restricted
class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['Shop_Name', 'Description', 'Street_Address', 'Suburb', 'City', 'ZipCode', 'Type', 'image']


class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset = ProductCategory.objects.all())
    class Meta:
        model = Product
        fields = ['Name', 'ProductType', 'Price', 'Description', 'category', 'Resale']

class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = ['AddImage', 'name', 'Stock', 'sizes']

ProductImageFormset = formset_factory(ProductImageForm, extra =1)
UpdateImageFormset = modelformset_factory(ProductImage, fields = ('AddImage', 'name', 'Stock', 'sizes'))

class QuantityForm(forms.Form):
    quantity = quantity = forms.IntegerField(initial = 0, widget = forms.NumberInput(attrs = {'style': 'width:60px', 'size': '10'}))
    FormId = forms.IntegerField(widget = forms.HiddenInput(), required = False)
    ProductId = forms.IntegerField(widget = forms.HiddenInput(), required = False)

class CheckoutSignUpForm(UserCreationForm):
    email = forms.EmailField()
    contact = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'contact','password1', 'password2', ]
