from .models import Shop, Product, ProductCategory, ShoppingCartOrder, OrderItem, Inventory, ProductImage
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
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
#from .documents import CategoryDocument, ShopDocument
from django.urls import reverse
from .tasks import OrderMessage
from profiles.models import ProgressBar
from django_popup_view_field.registry import registry_popup_view
from .popups import SizePopupView


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
    PopularCategories = sorted(PopularityList, key = keyfunc, reverse = True)
    PopularCategoryList =PopularCategories[:3]

    #orderting the products by most bought
    PopularProducts = []
    for cat, num in PopularCategoryList:
        for pro in cat.products.all():
            popularity = pro.orders.all().count()
            PopularProducts.append((pro, popularity))

    SortedProducts = sorted(PopularProducts, key = keyfunc, reverse = True)
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
        attr_id = int(request.session['item'])
        try:
            sizes = request.session['item_size']
        except:
            if not ProductImage.objects.get(id = attr_id).sizes:
                sizes = None
            else:
                return render(request, 'ecommerce/product-size-select.html', context = {'some_flag': True})
        colour = ProductImage.objects.get(id = attr_id).name
        #create pop up view to notify user the item is out of stock
        #if attribute.Stock < 1:
        #return
        QuantityForm = CartAddForm(request.POST)
        if QuantityForm.is_valid():
            Cart = Basket(request)
            Cart.AddToBasket(attr= attr_id, item = item, sizes = sizes, colour = colour, quantity = QuantityForm.cleaned_data['quantity'])
            request.session['cart'] = Cart.session['cart']
            request.session.modified = True
            message = messages.success(request, 'Contratulations, your product has been added to your cart')
            Description = item.Description
            context = {'item': item, 'Description': Description }
            return redirect('my-cart')

    else:
        try:
            del request.session['item_size']
            request.session.modified = True
        except:
            var = 1
        QuantityForm = CartAddForm(initial = {'FormId': 1})
        Description = item.Description
        data = {}
        for pro in item.images.all():
            if pro.sizes:
                size_data = pro.sizes.split(',')
                size_clone = [x.strip() for x in size_data]
                data[str(pro.id)] = {"stock": pro.Stock, "sizes": size_clone}
            else:
                data[str(pro.id)] = {"stock": pro.Stock, "sizes": None}
        #if request.is_ajax():
            #var2 = request.session['item']
            #variable = var2
        data = json.dumps(data)
        context = {'QuantityForm': QuantityForm, 'item': item, 'Description': Description, 'ProductSize': data }
        return render(request, 'ecommerce/product-page.html', context)

def Cart(request):
    cart = Basket(request)
    CartContents = cart.CartList()
    if request.method == 'GET':
        trolley = cart.basket
        #need to fix the message error
        if not trolley:
            #message = messages(request, 'Your cart is Empty, add items to your bag by exploring our great product catalogues')
            message = 'Silly message'
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
                item_id = CartContents[i][0]
                quantity = CartContents[i][1]
                price = CartContents[i][2]
                attribute_id = CartContents[i][3]
                initial.append({'quantity': quantity, 'FormId': attribute_id})

            formset = CartAddFormFormSet(initial = initial)
            goods = [Product.objects.get(id = x[0])for x in CartContents]
            size = len(CartContents)
            image_id = int(request.session['item'])
            cost = 0
            sizes = []
            colours = []
            for vars in trolley.values():
                cost = cost + int(vars['quantity'])*float(vars['Price'])
                request.session['cost'] = cost
                request.session.modified = True
                sizes.append(vars['size'])
                colours.append(vars['colour'])
            cost = request.session['cost']
            context = {'CartContents': CartContents, 'size': size, 'formset': formset, 'goods': goods, 'image_id': image_id, 'cost': cost, 'trolley': trolley, 'sizes': sizes, 'colours': colours}
            return render(request, 'ecommerce/cart.html', context)

    elif request.method == 'POST':
        CartContents = cart.CartList()
        initial = []
        for i in range(len(CartContents)):
            item_id = CartContents[i][0]
            quantity = CartContents[i][1]
            price = CartContents[i][2]
            attribute_id = int(CartContents[i][3])
            initial.append({'quantity': quantity, 'FormId': attribute_id})
        CartAddFormFormSet = formset_factory(CartAddForm)
        formset = CartAddFormFormSet(request.POST)
        trolley = cart.basket
        i = 0
        for form in formset.forms:
            if form.is_valid():
                item = CartContents[i][0]
                trolley[str(attribute_id)]['quantity'] = form.cleaned_data['quantity']
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
        id = id
        cart.Remove(id)
        request.session['cart'] = trolley
        request.session.modified = True
        return redirect('my-cart')


@login_required
def Checkout(request):
    trolley = request.session['cart']
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        details = {}
        if form.is_valid():
            details['Street_Address'] = form.cleaned_data['Street_Address']
            details['Suburb'] = form.cleaned_data['Suburb']
            details['City'] = form.cleaned_data['City']
            details['ZipCode'] = form.cleaned_data['ZipCode']
            cart_account = get_object_or_404(Account, user = request.user)
            shoppingcart = ShoppingCartOrder.objects.create(Owner = cart_account)
            for key, value in trolley.items():
                orderitem = OrderItem.objects.create(product = Product.objects.get(id = int(value['item_id'])), quantity = value['quantity'], attribute = ProductImage.objects.get(id =int(key)).name)
                shoppingcart.CartOrder.add(orderitem.id)
            shoppingcart.save()
            cart_id = shoppingcart.id
            progress_bar = ProgressBar.objects.create(account = cart_account, cart_id = cart_id )
            progress_bar.save()
            for item in shoppingcart.CartOrder.all():
                obj = item.product
                shop = obj.shop
                inventory = get_object_or_404(Inventory, shop = shop)
                item_id = item.id
                inventory.Messages(cart_id, item_id)
                inventory.save()
            request.session['shipping'] = details
            request.session['cart'] = {}
            request.session.modified = True
            #add a flash message here to tell the user their order is being processed and they will
            #find their reference number below.
            return redirect('account')
    else:
        form = CheckoutForm()
        cost = 0
        for vars in trolley.values():
            cost = cost + int(vars['quantity'])*float(vars['Price'])
            request.session['cost'] = cost
            request.session.modified = True
    context = {'form': form, 'cost': cost}
    return render(request, 'ecommerce/checkout.html', context)

def AjaxView(request):
        #return the item id, and the hash of the session_id using request.session.session_key

    if request.method == 'POST':
        data = request.POST
        image_id = data['id']
        var1 = data['var1']
        try:
            del request.session['item_size']
        except:
            var = 1
        #var1 = request.session['var1']
        #if var1 == request.session['var1']:
        request.session['item'] = image_id
        request.session.modified = True
        return HttpResponse(data)
    if request.method == 'GET':
        v = request.session.session_key
        var1 = hash(v)
        #here i am violating my rule of only calling the calling the session by Basket(request)
        request.session['var1'] = var1
        request.session.modified = True
        data = {'var1': var1}
        data = json.dumps(data)
        return HttpResponse(data)

""" This Ajax call is to determine the number of items in the basket. A try and except block is used to
prevent an internal server error should the user not have a basket"""
def AddToCartAjax(request):
    if request.is_ajax():
        if request.method == 'GET':
            try:
                cart= request.session['cart']
                num = len(cart)
                data = json.dumps({'num':num})
                return HttpResponse(data)
            except Exception:
                data = json.dumps({'num':0})
                return HttpResponse(data)

def AjaxSize(request):
        #return the item id, and the hash of the session_id using request.session.session_key

    if request.method == 'POST':
        data = request.POST
        size = data['id']
        #var1 = request.session['var1']
        #if var1 == request.session['var1']:
        request.session['item_size'] = size
        request.session.modified = True
        return HttpResponse(data)
    if request.method == 'GET':
        v = request.session.session_key
        var1 = hash(v)
        #here i am violating my rule of only calling the calling the session by Basket(request)
        request.session['var1'] = var1
        request.session.modified = True
        data = {'var1': var1}
        data = json.dumps(data)
        return HttpResponse(data)



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


def Searching(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query:
            client = Elasticsearch()
            s = Search(using = client, index = 'products').query('multi_match', query = query, fields = ['Name', 'ProductType', 'Description'], fuzziness = 1)
            queryset = []
            for hit in s:
                p = Product.objects.get(id = hit.meta.id)
                queryset.append(p)


            cats = Search(using = client, index = 'categories').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            catqueryset = []
            for hit in cats:
                c = ProductCategory.objects.get(id = hit.meta.id)
                catqueryset.append(c)

            shops = Search(using = client, index = 'shops').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            shopqueryset = []
            for hit in shops:
                var = Shop.objects.get(id = hit.meta.id)
                catqueryset.append(var)

            context = {'catqueryset': catqueryset, 'shopqueryset': shopqueryset,'queryset': queryset}
            return render(request, 'ecommerce/search.html', context)
        else:
            return render(request, 'ecommerce/no-search-results.html')

def AjaxSearch(request):
    if request.is_ajax():
        if request.method == 'POST':
            data = request.POST.get('SearchedItem')
            request.session['search'] = data
            request.session.modified = True
            data = json.dumps(data)
            return HttpResponse(data)
        elif request.method == 'GET':
            data = request.session['search']
            client = Elasticsearch()
            s = Search(using = client, index = 'products').query('multi_match', query = data, fields = ['Name', 'ProductType', 'Description'], fuzziness = 1)
            queryset = {}

            query = []
            for hit in s:
                p = Product.objects.get(id = hit.meta.id)
                queryset['Name'] = p.Name
                queryset['id'] = p.id
                queryset['type'] = 'product'
                queryset['url']= reverse('product-page', kwargs = {'id': p.id})
                query.append(queryset)

            '''
            cats = Search(using = client, index = 'categories').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            catqueryset = []
            for hit in cats:
                c = ProductCategory.objects.get(id = hit.meta.id)
                catqueryset.append(c)

            shops = Search(using = client, index = 'shops').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            shopqueryset = []
            for hit in shops:
                var = Shop.objects.get(id = hit.meta.id)
                catqueryset.append(var)
                '''
            data = json.dumps(query)
            return HttpResponse(data)
def AjaxAccept(request):
    pass
