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
    if request.method == 'GET':
        cart = Basket(request)
        trolley = cart.basket
        if not trolley:
            message = messages.something(request, 'Your cart is Empty, add items to your bag by exploring our great product catalogues')
            context = {'message': message}
            return render(request, 'ecommerce/cart.html', context)
        else:
            CartContents = cart.CartList()
            CartAddFormSet = formset_factory(CartAddForm, extra = len(CartContents)-1, can_delete = True)
            formset = CartAddFormSet()
            i = 0
            variable = request.session.get('CartForm')
            if not variable:
                variable = {}
            QForms = []
            for form in formset:
                item = CartContents[i][0]
                quantity = CartContents[i][1]
                price = CartContents[i][2]
                qform = CartAddForm(initial = {'quantity': quantity, 'FormId': item.id})
                variable[str(item.id)] = item.id
                request.session['CartForm'] = variable
                request.session.modified = True
                QForms.append([qform,item, quantity, price])
                i +=1
            context = {'CartContents': CartContents, 'QForms': QForms}
            return render(request, 'ecommerce/cart.html', context)

    elif request.method == 'POST':
        cart = Basket(request)
        CartAddFormSet = formset_factory(CartAddForm, extra = len(list(CartContents))-1, can_delete = True)
        formset = CartAddFormSet(request.POST)
        i = 0
        variable1 = request.session['CartForm']
        variable2 = variable1.values()
        if formset.is_valid():
            i = 0
            for form in formset:
                if form.cleaned_data in formset.deleted_forms:
                    cart.remove(Product.objects.get(id = variable2[i]))
                    request.session['cart'] = cart.save()
                    request.session.modified = True
                i += 1
            return render(request, 'ecommerce/checkout.html')
