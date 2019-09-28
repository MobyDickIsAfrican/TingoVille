from .models import Product, ProductImage

class Basket(object):
    def __init__(self, request):
        self.session = request.session
        self.basket = request.session.get('cart')
        if not self.basket:
            self.basket = self.session['cart'] = {}

    def AddToBasket(self, attr, item, sizes, colour, quantity= 1):
        attribute_id = str(attr)
        pro = ProductImage.objects.get(id = attr)
        colour = pro.name
        if pro.sizes:
            size_data = sizes
        else:
            size_data = None
        self.basket[attribute_id] = {'quantity': quantity, 'Price': str(item.Price), 'item_id': item.id, "size": size_data, 'colour':colour}

    def UpdateQuantity(self, item, quantity):
#the quantity will be a QuantityForm
    	self.basket[str(attribute_id)]['quantity'] = quantity

    def Remove(self, attribute_id):
        #the remove option will also be a form
        del self.basket[str(attribute_id)]

    def save(self):
        self.session['cart'] = self.basket
        self.session.modified = True
        return self.session['cart']
    def CartList(self):
        cart_keys = self.basket.keys()
        Attribute_ids = list(map(int, cart_keys))
        cart_values = self.basket.values()
        CartQuantities = []
        CartPrices = []
        Item_ids = []
        for item in cart_values:
            CartQuantities.append(item['quantity'])
            CartPrices.append(item['Price'])
            Item_ids.append(item['item_id'])

        cart_list =list(zip(Item_ids, CartQuantities, CartPrices, Attribute_ids))
        return cart_list
    #I need to add a functionality such that when a Shop owner deletes a product, it is removed from the basket.
