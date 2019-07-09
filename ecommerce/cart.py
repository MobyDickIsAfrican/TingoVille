from .models import Product

class Basket(object):
    def __init__(self, request):
        self.session = request.session
        self.basket = request.session.get('cart')
        if not self.basket:
            self.basket = self.session['cart'] = {}

    def AddToBasket(self, item, quantity= 1):
        itemid = str(item.id)
        if itemid not in self.basket:
        	self.basket[itemid] = {'quantity': quantity, 'Price': str(item.Price)}
        else:
        	self.basket[itemid]['quantity'] = quantity

    def UpdateQuantity(self, item, quantity):
#the quantity will be a QuantityForm
    	self.basket[str(item.id)]['quantity'] = quantity

    def Remove(self, item):
    #the remove option will also be a form
    	del self.basket[str(item.id)]

    def save(self):
        self.session['cart'] = self.basket
        self.session.modified = True
        return self.session['cart']
    def CartList(self):
        cart_keys = self.basket.keys()
        product_ids = list(map(int, cart_keys))
        BasketProductsList = []
        BasketProducts = Product.objects.filter(id__in = product_ids)
        for item in BasketProducts:
            BasketProductsList.append(item)
        cart_values = self.basket.values()
        CartQuantities = []
        CartPrices = []
        for item in cart_values:
            CartQuantities.append(item['quantity'])
            CartPrices.append(item['Price'])

        cart_list =list(zip(BasketProductsList, CartQuantities, CartPrices))
        return cart_list
