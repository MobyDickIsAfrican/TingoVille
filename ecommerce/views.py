from .models import Shop, Product, ProductCategory
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CartAddForm
from .cart import Basket
from django.forms import formset_factory

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

def Checkout(request):
    context = {}
    return render(request, 'ecommerce/checkout.html', context)
