from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRegisterForm, ProductForm, ShopForm, ProductImageForm, ProductImageFormset, UpdateImageFormset
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ecommerce.models import ProductImage, ShoppingCartOrder, Inventory, Product, Shop, compress, OrderItem
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
import logging
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.forms import inlineformset_factory
#this sign up view will be rendered when the user goes directly to the sign up page.

def SignUp(request):
    if request.method == 'POST':
        SignUpForm = UserRegisterForm(request.POST)
        if SignUpForm.is_valid():
            user = SignUpForm.save()
            user.refresh_from_db()
            user.account.First_Name = SignUpForm.cleaned_data.get('First_Name')
            user.account.Last_Name = SignUpForm.cleaned_data.get('Last_Name')
            user.account.contact = SignUpForm.cleaned_data.get('contact')
            user.account.Age = SignUpForm.cleaned_data.get('Age')
            user.account.email = SignUpForm.cleaned_data.get('email')
            user.account.save()
            username = SignUpForm.cleaned_data.get('username')
            messsage = messages.success(request, f'Welcome {username}, Start Shopping by adding goods to your trolley')
            new_user = authenticate(username=SignUpForm.cleaned_data['username'],
                                    password=SignUpForm.cleaned_data['password1'],
                                    email = SignUpForm.cleaned_data['email'])
            login(request, new_user)
            return redirect('home')
    else:
        SignUpForm = UserRegisterForm()

    context = {'SignUpForm': SignUpForm}
    return render(request, 'profiles/sign-up.html', context)
    
def CheckoutSignUp(request):
    if request.method == 'POST':
        SignUpForm = UserRegisterForm(request.POST)
        if SignUpForm.is_valid():
            user = SignUpForm.save()
            user.refresh_from_db()
            user.account.First_Name = SignUpForm.cleaned_data.get('First_Name')
            user.account.Last_Name = SignUpForm.cleaned_data.get('Last_Name')
            user.account.contact = SignUpForm.cleaned_data.get('contact')
            user.account.Age = SignUpForm.cleaned_data.get('Age')
            user.account.email = SignUpForm.cleaned_data.get('email')
            user.account.save()
            username = SignUpForm.cleaned_data.get('username')
            messsage = messages.success(request, f'Welcome {username}, Start Shopping by adding goods to your trolley')
            new_user = authenticate(username=SignUpForm.cleaned_data['username'],
                                    password=SignUpForm.cleaned_data['password1'],
                                    email = SignUpForm.cleaned_data['email'])
            login(request, new_user)
            return redirect('checkout')
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
            try:
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
            except Exception:
                request.session['cart'] = {}
                return LoginView(request, *args, **kwargs)
        return Inner

@method_decorator(Login_session(vars), name='dispatch')
class LoginView(auth_views.LoginView):
    def CheckLogin(self):
        if self.request.method == 'POST':
            logging.basicConfig(filename = 'UserLogin.log', level = logging.INFO, format = '%(message)s')
            date = datetime.now()
            username = self.request.POST['username']
            logging.info(f'{username}, {date}')
    def form_valid(self, form):
        self.CheckLogin()
        return super(LoginView, self).form_valid(form)
    #check to see if the user is coming from having submitted checkout button,
    #if yes the sign up button will redirect to the checkout
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            from_checkout = self.request.session['checkout']
        except:
            from_checkout = False
        self.request.session['checkout'] = False
        self.request.session.modified = True
        context["from_checkout"] = from_checkout
        return context


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
            #inventory = Inventory(shop = MyShop)
            #inventory.save()
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
                img = form.cleaned_data.get('AddImage')
                image = compress(img)
                stock = form.cleaned_data.get('Stock')
                sizes = form.cleaned_data.get('sizes')
                if name and image:
                    ProductImage(name = name, AddImage =image, Stock = stock, image = x, sizes = sizes).save()
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
        messages = user_account.ProcessedOrders
        cancel_message = user_account.CancelledOrders
        notifications = []
        for item in messages:
            try:
                order_id = item[1]
                order = OrderItem.objects.get(id = order_id)
                number = order.quantity
                attribute = order.attribute
                pro_name = order.product.Name
                notification = f'Your order for {number} {attribute} {pro_name} is being processed'
                notifications.append(notification)
            except:
                var = 'random'
        user_account.CheckProcessedFully()
        user_account.CancelledOrders = []
        user_account.ProcessedOrders = []
        user_account.save(update_fields = ['ProcessedOrders'])
        context = {'query': query, 'dates': dates, 'numbers': numbers, 'AccountDetails': AccountDetails, 'notifications': notifications, 'cancel_message':cancel_message}
        return render(request, 'profiles/account.html', context)

    else:
        return render(request, 'profiles/account-none.html')

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def UpdateProduct(request, id):
    product_instance = Product.objects.get(id = id)
    ProductInlineformset = inlineformset_factory(Product, ProductImage, ProductImageForm, fields = ('AddImage', 'name', 'Stock', 'sizes'), extra=0, can_delete=True)
    if request.method == 'POST':
        RegisterProductForm = ProductForm(request.POST, instance = product_instance)
        Imageformset = ProductInlineformset(request.POST, request.FILES, instance = product_instance)
        u = RegisterProductForm.is_valid()
        v = Imageformset.is_valid()
        if u and v:
            RegisterProductForm.save()
            Imageformset.save()
            message = messages.success(request, f'Congratulations, your product has been updated')
            return redirect('my-shop')
    else:
        RegisterProductForm = ProductForm(request.GET or None, instance = product_instance)
        Imageformset = ProductInlineformset(instance = product_instance)
    context = {'RegisterProductForm':RegisterProductForm, 'Imageformset':Imageformset}
    return render(request, 'profiles/update-product.html', context)

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def InventoryView(request):
    this_user = request.user
    this_account = get_object_or_404(Account, user = this_user)
    this_shop = get_object_or_404(Shop, name = this_account)
    id = this_shop.inventory.id
    inventory = Inventory.objects.get(id = id)
    acceptedproducts =[]
    #inventory.PendingOrders = []
    #inventory.PendingProductIds = []
    #inventory.PendingOrderIds = []
    #inventory.PendingObjectId = []
    #inventory.save(update_fields = ['PendingOrders', 'PendingOrderIds', 'PendingProductIds', 'PendingObjectId'])
    for p in Product.objects.filter(id__in = inventory.AcceptedProductIds):
        acceptedproducts.append(p.id)
    PendingQuerySet = list(zip(inventory.PendingOrders, inventory.PendingProductIds, inventory.PendingOrderIds, inventory.PendingObjectId, Product.objects.filter(id__in = inventory.PendingProductIds)))
    AcceptedQuerySet = list(zip(inventory.AcceptedOrders, inventory.AcceptedProductIds, inventory.AcceptedUsersIds, acceptedproducts, inventory.AcceptedObjectId))
    shop = inventory.shop
    QForms = []
    #inventory.PendingOrders = []
    #inventory.PendingProductIds = []
    #inventory.PendingOrderIds = []
    #inventory.save(update_fields = ['PendingOrders', 'PendingProductIds', 'PendingOrderIds'])
    items = []
    for item in shop.product_set.all():
        for item2 in item.images.all():
            form = QuantityForm(initial = {'FormId': item.id, 'ProductId': item2.id})
            QForms.append(form)
            items.append(item2)
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
        context = {'QForms': QForms, 'PendingQuerySet': PendingQuerySet, 'AcceptedQuerySet': AcceptedQuerySet, 'inventory': inventory, 'items': items}
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
                return redirect('inventory')
                # i need to add Stock form field to the Register - Product template.

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def AcceptOrder(request, inventory_id ,cart_id, order_id):
    inventory = Inventory.objects.get(id = inventory_id)
    cart = ShoppingCartOrder.objects.get(id = cart_id)
    account_user = cart.Owner
    inventory.Approve(order_id)
    account_user.Message(cart_id, order_id)
    return redirect('inventory')

@login_required
def OrderTracker(request):
    user = request.user
    user_account = get_object_or_404(Account, user = user)
    progress_bar_queryset = user_account.progressbars.all()
    Refs = []
    for item in progress_bar_queryset:
        cart = ShoppingCartOrder.objects.get(id = item.cart_id)
        Ref = cart.ReferenceNumber()
        Refs.append(Ref)
    context = {'progress_bar_queryset': progress_bar_queryset, 'Refs': Refs}
    return render(request, 'ecommerce/track-order.html', context)

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def DeclineOrder(request, order_id, cart_id):
    instance = OrderItem.objects.get(id = order_id)
    product = instance.product
    shop = product.shop
    inventory_id = get_object_or_404(Inventory, shop = shop).id
    product_name = product.Name
    cart = ShoppingCartOrder.objects.get(id = cart_id)
    user_account = cart.Owner
    user_account.Declined(product_name)
    inventory = Inventory.objects.get(id = inventory_id)
    inventory.Remove(order_id)
    #instance.delete()
    return redirect('inventory')
