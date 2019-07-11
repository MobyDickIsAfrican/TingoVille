from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, ProductForm, ShopForm, ProductImageForm, ProductImageFormset
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ecommerce.models import ProductImage
from django.contrib.auth import views
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from functools import wraps
from ecommerce.views import Product
#this sign up view will be rendered when the user goes directly to the sign up page.

def SignUp(request):
    if request.method == 'POST':
        SignUpForm = UserRegisterForm(request.POST)
        if SignUpForm.is_valid():
            SignUpForm.save()
            username = SignUpForm.cleaned_data.get('username')
            messsage = messages.success(request, f'Welcome {username}, Start Shopping by adding goods to your trolley')
            return redirect('home')
    else:
        SignUpForm = UserRegisterForm()

    context = {'SignUpForm': SignUpForm}
    return render(request, 'profiles/sign-up.html', context)

class Login_session(object):
    def __init__(self, vars):
        self.vars = vars
    def __call__(self, LoginView):
        @wraps(LoginView)
        def Inner(request, *args, **kwargs):
            self.vars = request.session['cart']
            back_up_session = {}
            for key, var in self.vars.items():
                try:
                    back_up_session[key] = var
                except KeyError:
                    pass
            response = LoginView(request, *args, **kwargs)
            for key2, value in back_up_session.items():
                request.session[key2] = value
            return response
        return Inner

@method_decorator(Login_session(vars), name='dispatch')
class LoginView(auth_views.LoginView):
    pass

@login_required
#need to build a custom decorator to check if a user does not already have a shop.
def RegisterShop(request):
    if request.method == 'POST':
        RegisterShopForm = ShopForm(request.POST)
        if RegisterShopForm.is_valid():
            RegisterShopForm.save()
            Shop_Name = RegisterShopForm.cleaned_data['Shop_Name']
            message = messages.success(request, f'Congratulations your Shop, {Shop_Name} has been created. Start adding products! We have created an inventory for you')
            return redirect('my-shop')
    else:
        #if request.user.account.shop.all().exists():
            #return redirect('my-shop')
        RegisterShopForm = ShopForm()

    context = {'RegisterShopForm': RegisterShopForm}
    return render(request, 'profiles/register-shop.html', context)


def TestProduct(user):
    if user.is_authenticated:
        return user.account.shop.all().exists()
    else:
        return False

#@login_required
#@user_passes_test(TestProduct, login_url ='register-shop')
def RegisterProduct(request):
    if request.method == 'POST':
        RegisterProductForm = ProductForm(request.POST)
        Imageformset = ProductImageFormset(request.POST, request.FILES)
        u = RegisterProductForm.is_valid()
        v = Imageformset.is_valid()
        if u and v:
            RegisterProductForm.save()
            x = RegisterProductForm.save()
            for form in Imageformset:
                name = form.cleaned_data.get('name')
                image = form.cleaned_data.get('AddImage')
                if name and image:
                    ProductImage(name = name, AddImage =image, image = x).save()
            message = messages.success(request, f'Congratulations, your product has been captured. You can now view your shop and inventory. To update your stock go to your Inventory')
            return redirect('my-shop')
    else:
        RegisterProductForm = ProductForm()
        Imageformset = ProductImageFormset(request.GET or None)
    context = {'RegisterProductForm':RegisterProductForm, 'Imageformset':Imageformset}
    return render(request, 'profiles/register-product.html', context)

def Account(request, id):
    return render(request, 'profiles/accoount.html')
