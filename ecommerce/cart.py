

class Basket(object):
    def __init__(self, request):
        self.session = request.session
        self.basket = request.session.get('cart')
        if not self.basket:
            self.basket = self.session['cart'] = {}

    def AddToBasket(self, item, quantity= 1):
        itemid = str(item.id)
        if itemid not in self.basket:
        	self.basket[itemid] = {'quantity': str(quantity), 'Price': str(item.Price)}
        else:
        	self.basket[itemid]['quantity'] += quantity

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
 #self.cart[product_id] = {'quantity': 0,
                                  #'price': str(product.price)}
