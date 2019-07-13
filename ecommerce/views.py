from .models import Shop, Product, ProductCategory, ShoppingCartOrder, OrderItem
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CartAddForm
from .cart import Basket
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required
from .forms import CheckoutForm
from django.views.generic import View
from django.http import HttpResponse
from profiles.models import Account

def keyfunc(x):
    return x[1]

def Home(request):
    C = ProductCategory.objects.all()
    PopularityList = []
    for c in C:
        P = c.products.all()
        sum = 0
        for p in P:
            sum = sum + p.orders.all().count()

        PopularityList.append((c, sum))
    PopularCategories = sorted(PopularityList, key = keyfunc)
    PopularCategoryList =PopularCategories[:7]

    #orderting the products by most bought
    PopularProducts = []
    for cat, num in PopularCategoryList:
        for pro in cat.products.all():
            popularity = pro.orders.all().count()
            PopularProducts.append((pro, popularity))

    SortedProducts = sorted(PopularProducts, key = keyfunc)
    PopularList = SortedProducts[:7]
    Fresh = []
    count = 0
    for item in Product.objects.all():
        Fresh.append(item)
        count += 1
        if count == 7:
            break
    context = {'PopularCategoryList': PopularCategoryList, 'Fresh': Fresh, 'PopularList': PopularList}
    return render(request, 'ecommerce/Home.html', context)

def MyShop(request):
    context = {}
    return render(request, 'ecommerce/my-shop.html', context)

def ProductPage(request, id):
    item = get_object_or_404(Product, id = id)
    i = item.images.all().count()
    if request.method == 'POST':
        QuantityForm = CartAddForm(request.POST)
        if QuantityForm.is_valid():
            Cart = Basket(request)
            Cart.AddToBasket(item = item, quantity = QuantityForm.cleaned_data['quantity'])
            request.session['cart'] = Cart.session['cart']
            request.session.modified = True
            message = messages.success(request, 'Contratulations, your product has been added to your cart')
            Description = item.Description
            context = {'item': item, 'Description': Description }
            return redirect('my-cart')

    else:
        QuantityForm = CartAddForm(initial = {'FormId': 1})
        Description = item.Description
        #if request.is_ajax():
            #var2 = request.session['item']
            #variable = var2
        context = {'QuantityForm': QuantityForm, 'item': item, 'Description': Description }
        return render(request, 'ecommerce/product-page.html', context)

def Cart(request):
    cart = Basket(request)
    CartContents = cart.CartList()
    if request.method == 'GET':
        trolley = cart.basket
        if not trolley:
            message = messages.something(request, 'Your cart is Empty, add items to your bag by exploring our great product catalogues')
            context = {'message': message}
            return render(request, 'ecommerce/cart.html', context)
        else:
            #variable = request.session.get('CartForm')
            #if not variable:
                #variable = {}
            QForms =[]
            initial = []
            CartAddFormFormSet = formset_factory(CartAddForm, extra = len(CartContents))
            for i in range(len(CartContents)):
                item = CartContents[i][0]
                quantity = CartContents[i][1]
                price = CartContents[i][2]
                initial.append({'quantity': quantity, 'FormId': item.id})

            formset = CartAddFormFormSet(initial = initial)
            goods = [x[0] for x in CartContents]
            size = len(CartContents)
            context = {'CartContents': CartContents, 'size': size, 'formset': formset, 'goods': goods}
            return render(request, 'ecommerce/cart.html', context)

    elif request.method == 'POST':
        CartContents = cart.CartList()
        initial = []
        for i in range(len(CartContents)):
            item = CartContents[i][0]
            quantity = CartContents[i][1]
            price = CartContents[i][2]
            initial.append({'quantity': quantity, 'FormId': item.id})
        CartAddFormFormSet = formset_factory(CartAddForm)
        formset = CartAddFormFormSet(request.POST)
        trolley = cart.basket
        i = 0
        for form in formset.forms:
            if form.is_valid():
                item = CartContents[i][0]
                trolley[str(item.id)]['quantity'] = form.cleaned_data['quantity']
                i += 1
        request.session['cart'] = trolley
        request.session.modified = True
        return redirect('checkout')

def CartItemDelete(request, id):
    if request.method == 'GET':
        cart = Basket(request)
        trolley = cart.basket
        if not trolley:
            return redirect('my-cart')
        cart.Remove(Product.objects.get(id = id))
        request.session['cart'] = trolley
        request.session.modified = True
        return redirect('my-cart')


@login_required
def Checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        details = {}
        if form.is_valid():
            details['Street_Address'] = form.cleaned_data['Street_Address']
            details['Suburb'] = form.cleaned_data['Suburb']
            details['City'] = form.cleaned_data['City']
            details['ZipCode'] = form.cleaned_data['ZipCode']
            trolley = request.session['cart']
            cart_account = get_object_or_404(Account, user = request.user)
            shoppingcart, status = ShoppingCartOrder.objects.get_or_create(Owner = cart_account)
            for key, value in trolley.items():
                orderitem, status = OrderItem.objects.get_or_create(product = Product.objects.get(id = int(key)), quantity = value['quantity'])
                shoppingcart.CartOrder.add(orderitem.id)
            shoppingcart.save()

            request.session['shipping'] = details
            request.session.modified = True
            #add a flash message here to tell the user their order is being processed and they will
            #find their reference number below.
            return redirect('account')
    else:
        form = CheckoutForm()
    context = {'form': form}
    return render(request, 'ecommerce/checkout.html', context)

class AjaxView(View):
    def post(self, request, kwargs):
        #return the item id, and the hash of the session_id using request.session.session_key
        v = request.session.session_key
        var1 = hash(v)
        #here i am violating my rule of only calling the calling the session by Basket(request)
        request.session['var1'] = var1
        request.session.modified = True
        data = {'var1': var1}
        data = json.dumps(data)
        return HttpResponse(data)



def json_data(request):
    if request.is_ajax():
        if request.method == 'POST':
            data = request.body
            data = json.loads(data)
            image_id = data['id']
            var1 = data['var1']
            if var1 == request.session['var1']:
                #here i am violating my rule of only calling the calling the session by Basket(request)
                request.session['item'] = image_id
                request.session.modified = True

def CategoryView(request):
    #make a query for all Categories
    #now i need to get a default image for the CategoryView - this can be done in the models
    query = ProductCategory.objects.all()

    context = {'query': query}
    return render(request, 'ecommerce/categories.html', context)
    
def CategoryProducts(request, id):
    cats = ProductCategory.objects.get(id = id)
    pro = cats.products.all()
    context = {'cats': cats, 'pro': pro}
    return render(request, 'ecommerce/category-products.html', context)
