from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, ProductForm, ShopForm, ProductImageForm, ProductImageFormset
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ecommerce.models import ProductImage
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

@login_required
#need to build a custom decorator to check if a user does not already have a shop.
def RegisterShop(request, id):
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
def RegisterProduct(request, id):
    if request.method == 'POST':
        RegisterProductForm = ProductForm(request.POST)
        Imageformset = ProductImageFormset(request.POST)
        if RegisterProductForm.is_valid():
            RegisterProductForm.save()
            if Imageformset.is_valid():
                for form in Imageformset:
                    name = form.cleaned_data.get('name')
                    image = form.cleaned_data.get('AddImage')
                    if name:
                        ProductImage(name = name, AddImage =image).save()

            message = messages.success(request, f'Congratulations, your product has been captured. You can now view your shop and inventory. To update your stock go to your Inventory')
            return redirect('my-shop')
    else:
        RegisterProductForm = ProductForm()
        Imageformset = ProductImageFormset(request.GET or None)
    context = {'RegisterProductForm':RegisterProductForm, 'Imageformset':Imageformset}
    return render(request, 'profiles/register-product.html', context)
