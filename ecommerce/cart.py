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
        cart_values = self.basket.values()
        CartQuantities = []
        CartPrices = []
        for item in cart_values:
            CartQuantities.append(item['quantity'])
            CartPrices.append(item['Price'])

        cart_list =list(zip(product_ids, CartQuantities, CartPrices))
        return cart_list
    #I need to add a functionality such that when a Shop owner deletes a product, it is removed from the basket.
