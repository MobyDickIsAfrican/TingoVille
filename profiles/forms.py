from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from ecommerce.models import Shop, Product
import itertools
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from ecommerce.models import ProductImage

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    contact = forms.IntegerField()
    #need to validate that the contact is a valid phone number

    class Meta:
        model = User
        fields = ['username', 'email', 'contact','password1', 'password2', ]

#allow users to register their shops. this will need to be restricted
class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['Shop_Name', 'Description', 'Delivery_Location']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['Name', 'ProductType', 'Price', 'Stock', 'Description' ]
        '''
    def clean_Description(self):
        descriptiondata = self.cleaned_data['Description']
        try:
            commalist = descriptiondata.split(';')
        except Exception:
            raise forms.ValidationError('Your Description does not have semi colons')

        finally:
            RawList = []
            contents = {}
            def NotZero(x):
                return x == ' '
            for item in commalist:
                #try:

                raw_key, raw_value = item.split(':')
                var1 = itertools.dropwhile(NotZero, raw_key)
                raw_key = ''.join(list(itertools.dropwhile(NotZero, var1[::-1])))
                raw_key = raw_key[::-1]
                var2 = itertools.dropwhile(NotZero, raw_key)
                raw_value = ''.join(list(itertools.dropwhile(NotZero, var2[::-1])))
                raw_value = raw_value[::-1]
                raw_key.capitalize()
                raw_value.capitalize()
                contents[raw_key]  = raw_value
                '''
                    #raise forms.ValidationError('You forgot (:) in your description')



class ProductImageForm(forms.ModelForm):

    class Meta:
        model = ProductImage
        fields = ['AddImage', 'name']

ProductImageFormset = formset_factory(ProductImageForm, extra =1)
