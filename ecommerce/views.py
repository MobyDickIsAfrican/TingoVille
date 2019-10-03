from .models import Shop, Product, ProductCategory, ShoppingCartOrder, OrderItem, Inventory, ProductImage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import CartAddForm
from .cart import Basket
from django.forms import formset_factory
from django.contrib.auth.decorators import login_required, user_passes_test
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
import certifi
from django_user_agents.utils import get_user_agent
from django.conf import settings
from django.core.paginator import Paginator
import logging

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
    PopularList = SortedProducts[:4]
    Fresh = []
    count = 0
    for item in reversed(Product.objects.all()):
        Fresh.append(item)
        count += 1
        if count == 4:
            break
    Cat_1 = ProductCategory.objects.get(CategoryName = 'Resale Clothing - Women')
    Cat_2 = ProductCategory.objects.get(CategoryName = 'Resale Clothing - Men')
    Women_Resale = Cat_1.products.all()[:4]
    Men_Resale = Cat_2.products.all()[:4]
    query = query = ProductCategory.objects.all()
    query_1 = query[:4]
    query_2 = query[4:]
    context = {'PopularCategoryList': PopularCategoryList, 'Fresh': Fresh, 'PopularList': PopularList, 'Women_Resale': Women_Resale, 'Men_Resale':Men_Resale, 'query_1': query_1,  'query_2': query_2}
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(request, 'ecommerce/Home-mobile.html', context)
    return render(request, 'ecommerce/Home.html', context)

def TestProduct(user):
    if user.is_authenticated:
        return user.account.shop.all().exists()
    else:
        return False

@login_required
@user_passes_test(TestProduct, login_url ='register-shop')
def MyShop(request):
    user = request.user
    user_account = get_object_or_404(Account, user = user)
    shop = get_object_or_404(Shop, name = user_account)
    items = shop.product_set.all()
    context = {'items': items}
    return render(request, 'ecommerce/my-shop.html', context)

def ProductPage(request, id):
    item = get_object_or_404(Product, id = id)
    if request.method == 'POST':
        attr_id = int(request.session['item'])
        value = True
        try:
            sizes = request.session['item_size']
        except:
            if not ProductImage.objects.get(id = attr_id).sizes:
                sizes = None
                value = None
            else:
                value = False
        colour = ProductImage.objects.get(id = attr_id).name
        #create pop up view to notify user the item is out of stock
        #if attribute.Stock < 1:
        #return
        QuantityForm = CartAddForm(request.POST)
        QuantityForm.Size = value
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
        QuantityForm = CartAddForm(initial = {'FormId': 1})

    i = item.images.all().first().id
    request.session['item'] = i
    request.session.modified = True
    try:
        del request.session['item_size']
        request.session.modified = True
    except:
        var = 1
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
    shop = item.shop
    context = {'QuantityForm': QuantityForm, 'item': item, 'Description': Description, 'ProductSize': data, 'shop': shop }
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(request, 'ecommerce/product-page-mobile.html', context)
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
            user_agent = get_user_agent(request)
            if user_agent.is_mobile:
                return render(request, 'ecommerce/cart-mobile.html', context)
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
        request.session['checkout'] = True
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
            messages = []
            for key, value in trolley.items():
                p = Product.objects.get(id = int(value['item_id']))
                orderitem = OrderItem.objects.create(product = p, quantity = value['quantity'], attribute = ProductImage.objects.get(id =int(key)).name, size = value['size'])
                shoppingcart.CartOrder.add(orderitem.id)
            shoppingcart.save()
            messages.append(shoppingcart.ReferenceNumber())
            logging.basicConfig(filename = 'Checkout.log', level = logging.INFO, format = '%(message)s')
            logging.info(f'{messages}')
            cart_id = shoppingcart.id
            progress_bar = ProgressBar.objects.create(account = cart_account, cart_id = cart_id )
            progress_bar.save()
            for item in shoppingcart.CartOrder.all():
                obj = item.product
                shop = obj.shop
                inventory = get_object_or_404(Inventory, shop = shop)
                item_id = item.id
                inventory.Messages(cart_id, item_id)
            request.session['shipping'] = details
            request.session['cart'] = {}
            request.session.modified = True
            #add a flash message here to tell the user their order is being processed and they will
            #find their reference number below.
            return redirect('account')
    else:
        form = CheckoutForm()
        cost = 0
        number = 0
        for vars in trolley.values():
            cost = cost + int(vars['quantity'])*float(vars['Price'])
            request.session['cost'] = cost
            request.session.modified = True
            number +=1
    context = {'form': form, 'cost': cost, 'number': number}
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
    user_agent = get_user_agent(request)
    if user_agent.is_mobile:
        return render(request, 'ecommerce/categories-mobile.html', context)
    return render(request, 'ecommerce/categories.html', context)

def CategoryProducts(request, id):
    cats = ProductCategory.objects.get(id = id)
    pros = cats.products.all()
    paginator = Paginator(pros, 25)
    page = request.GET.get('page')
    pro = paginator.get_page(page)
    context = {'cats': cats, 'pro': pro}
    return render(request, 'ecommerce/category-products.html', context)

http_auth = settings.HTTP_AUTH
host = settings.HOST

def Searching(request):
    if request.method == 'GET':
        query = request.GET.get('q')
        if query:
            client = Elasticsearch(hosts = host, http_auth = http_auth, use_ssl=True, ca_certs=certifi.where())
            s = Search(using = client, index = 'products').query('multi_match', query = query, fields = ['Name', 'ProductType', 'Description'], fuzziness = 1)
            queryset = []
            for hit in s:
                try:
                    p = Product.objects.get(id = hit.meta.id)
                    queryset.append(p)
                except:
                    p = None

            cats = Search(using = client, index = 'categories').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            catqueryset = []
            for hit in cats:
                try:
                    c = ProductCategory.objects.get(id = hit.meta.id)
                    catqueryset.append(c)
                except:
                    c = None

            shops = Search(using = client, index = 'shops').query('multi_match', query = query, fields = ['Name'], fuzziness = 1)
            shopqueryset = []
            for hit in shops:
                try:
                    var = Shop.objects.get(id = hit.meta.id)
                    catqueryset.append(var)
                except:
                    var = None

            context = {'catqueryset': catqueryset, 'shopqueryset': shopqueryset,'queryset': queryset}
            user_agent = get_user_agent(request)
            if user_agent.is_mobile:
                return render(request, 'ecommerce/search-mobile.html', context)
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
            client = Elasticsearch(hosts = host, http_auth = http_auth, use_ssl=True, ca_certs=certifi.where())
            s = Search(using = client, index = 'products').query('multi_match', query = data, fields = ['Name', 'ProductType', 'Description'], fuzziness = 1)
            queryset = {}

            query = []
            for hit in s:
                try:
                    p = Product.objects.get(id = hit.meta.id)
                    queryset['Name'] = p.Name
                    queryset['id'] = p.id
                    queryset['type'] = 'product'
                    queryset['url']= reverse('product-page', kwargs = {'id': p.id})
                    query.append(queryset)
                except:
                    p = None

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

def HowItWorks(request):
    return render(request, 'ecommerce/howitworks.html', context= {})
    
def About(request):
    return render(request, 'ecommerce/about.html', context= {})
     
def Returns(request):
    return render(request, 'ecommerce/returns.html', context = {})
 
def Terms(request):
    return render(request, 'ecommerce/terms.html', context = {})

def Help(request):
    return render(request, 'ecommerce/seller-help.html', context = {})

def Empty(request):
    trolley = {}
    request.session['cart'] = trolley
    request.session.modified = True
    return redirect('my-cart')