from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, ProductForm, ShopForm, ProductImageForm, ProductImageFormset
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ecommerce.models import ProductImage, ShoppingCartOrder, Inventory, Product, Shop
from django.contrib.auth import views
from django.contrib.auth import views as auth_views
from django.utils.decorators import method_decorator
from functools import wraps
from .models import Account
from datetime import timedelta
from django.forms import formset_factory
from .forms import QuantityForm
from django.urls import reverse
from .models import ProgressBar
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
            shop_account = get_object_or_404(Account, user = request.user)
            MyShop = RegisterShopForm.save(commit = False)
            MyShop.name = shop_account
            MyShop.save()
            inventory = Inventory(shop = MyShop)
            inventory.save()
            Shop_Name = RegisterShopForm.cleaned_data['Shop_Name']
            message = messages.success(request, f'Congratulations your Shop, {Shop_Name} has been created. Start adding products! We have created an inventory for you')
            return redirect('my-shop')
    else:
        this_account = get_object_or_404(Account, user = request.user)
        if Shop.objects.filter(name = this_account).exists():
            return redirect('my-shop')
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

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def RegisterProduct(request):
    if request.method == 'POST':
        RegisterProductForm = ProductForm(request.POST)
        Imageformset = ProductImageFormset(request.POST, request.FILES)
        u = RegisterProductForm.is_valid()
        v = Imageformset.is_valid()
        if u and v:
            MyProduct = RegisterProductForm.save(commit = False)
            UserAccount = get_object_or_404(Account, user = request.user)
            UserShop = get_object_or_404(Shop, name = UserAccount)
            MyProduct.shop = UserShop
            MyProduct.save()
            x = RegisterProductForm.save()
            for form in Imageformset:
                name = form.cleaned_data.get('name')
                image = form.cleaned_data.get('AddImage')
                stock = form.cleaned_data.get('Stock')
                if name and image:
                    ProductImage(name = name, AddImage =image, Stock = stock, image = x).save()
            message = messages.success(request, f'Congratulations, your product has been captured. You can now view your shop and inventory. To update your stock go to your Inventory')
            return redirect('my-shop')
    else:
        RegisterProductForm = ProductForm()
        Imageformset = ProductImageFormset(request.GET or None)
    context = {'RegisterProductForm':RegisterProductForm, 'Imageformset':Imageformset}
    return render(request, 'profiles/register-product.html', context)

@login_required
def AccountView(request):
    #the Reference number is generated here, as the user will be redirected to this page when they place
    #an order. Secondly, the reference number has to be in this context.
    user_account = get_object_or_404(Account, user = request.user)
    if ShoppingCartOrder.objects.filter(Owner = user_account).exists():
        query = ShoppingCartOrder.objects.filter(Owner = user_account)
        dates = []
        numbers = []
        Delivery_Dates = []
        costs = []
        #i still need to a short order description here: 3x Red Shirt, 4x white Shoes.
        for item in query:
            dates.append(item.Date_Ordered.date())
            Delivery_Date = item.Date_Ordered.date() + timedelta(days = 3)
            Delivery_Dates.append(Delivery_Date)
            numbers.append(item.ReferenceNumber())
            cost = item.TotalCost()
            costs.append(cost)
        AccountDetails = list(zip(query, dates, numbers, Delivery_Dates, costs))
        user_account.Processed()
        user_account.CheckProcessedFully()
        context = {'query': query, 'dates': dates, 'numbers': numbers, 'AccountDetails': AccountDetails}
        return render(request, 'profiles/account.html', context)

    else:
        return render(request, 'profiles/account-none.html')

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def InventoryView(request, id):
    this_user = request.user
    this_account = get_object_or_404(Account, user = this_user)
    this_shop = get_object_or_404(Shop, name = this_account)
    id = this_shop.inventory.id
    inventory = Inventory.objects.get(id = id)
    acceptedproducts =[]
    for p in Product.objects.filter(id__in = inventory.AcceptedProductIds):
        acceptedproducts.append(p.id)
    PendingQuerySet = zip(inventory.PendingOrders, inventory.PendingProductIds, inventory.PendingOrderIds, inventory.PendingObjectId, Product.objects.filter(id__in = inventory.PendingProductIds))
    AcceptedQuerySet = list(zip(inventory.AcceptedOrders, inventory.AcceptedProductIds, inventory.AcceptedUsersIds, acceptedproducts, inventory.AcceptedObjectId))
    shop = inventory.shop
    QForms = []
    #inventory.PendingOrders = []
    #inventory.PendingProductIds = []
    #inventory.PendingOrderIds = []
    #inventory.save(update_fields = ['PendingOrders', 'PendingProductIds', 'PendingOrderIds'])
    for item in shop.product_set.all():
        for item2 in item.images.all():
            form = QuantityForm(initial = {'FormId': item.id, 'ProductId': item2.id})
            QForms.append(form)
    if request.method == 'GET':
        var = list(zip(inventory.AcceptedOrders, inventory.AcceptedProductIds, inventory.AcceptedUsersIds, inventory.AcceptedObjectId))
        if len(var) > 0:
            for x, y, z, k in var:
                inventory.AcceptedOrders.remove(x)
                inventory.AcceptedProductIds.remove(y)
                inventory.AcceptedUsersIds.remove(z)
                inventory.AcceptedObjectId.remove(k)
                inventory.save(update_fields = ['AcceptedOrders', 'AcceptedProductIds', 'AcceptedUsersIds', 'AcceptedObjectId'])
        shop = inventory.shop
        products = shop.product_set.all()
        context = {'products': products, 'QForms': QForms, 'PendingQuerySet': PendingQuerySet, 'AcceptedQuerySet': AcceptedQuerySet, 'inventory': inventory}
        return render(request, 'ecommerce/inventory.html', context)
    if request.method == 'POST':
        for form in QForms:
            form = QuantityForm(request.POST)
            if form.is_valid():
                product_id = form.cleaned_data['ProductId']
                item_id = form.cleaned_data['FormId']
                quantity = form.cleaned_data['quantity']
                products = shop.product_set.all()
                p = products.get(id = item_id)
                pro = p.images.get(id = product_id)
                pro.Stock = pro.Stock + quantity
                pro.save(update_fields = ['Stock'])
                return redirect('inventory', id = inventory.id)
                # i need to add Stock form field to the Register - Product template.

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def AcceptOrder(request, inventory_id ,cart_id, order_id):
    inventory = Inventory.objects.get(id = inventory_id)
    cart = ShoppingCartOrder.objects.get(id = cart_id)
    account_user = cart.Owner
    inventory.Approve(order_id)
    account_user.Message(cart_id, order_id)
    return redirect('inventory', id = inventory_id)

@login_required
def OrderTracker(request):
    user = request.user
    user_account = get_object_or_404(Account, user = user)
    progress_bar_queryset = user_account.progressbars.all()
    context = {'progress_bar_queryset': progress_bar_queryset}
    return render(request, 'ecommerce/track-order.html', context)
