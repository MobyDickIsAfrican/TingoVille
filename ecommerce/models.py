from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime
from profiles.models import Account



## creating a shop model for the seller. The AUTH_USER_MODEL is used to link the seller to the user who actually
## created the shop or sold the product.

class Shop(models.Model):
    name = models.ForeignKey(Account, on_delete = models.CASCADE, related_name = 'shop')
    #each user can have many shops
    Shop_Name = models.CharField(max_length = 30, unique = True)
    Description = models.TextField(max_length = 200)
    Delivery_Location = models.PointField(null=True, blank=True, srid = 4326)
    #srid = 4326 is the defaault and most popular
    created = models.DateTimeField(auto_now_add = True, blank = True)

    #add cool customiseable stuff for the seller to make shop feel organic.

    # Ask for preferred method of payment
    def __str__(self):
        return str(self.Shop_Name)

    ##def Payment_Options(self)
    ##return None

class ProductCategory (models.Model):
    CategoryName = models.CharField(max_length = 50, unique= True)

    def __str__(self):
        return self.CategoryName

    class Meta:
        ordering = ['CategoryName']
        #the categories are ordered in alphabetical order
        verbose_name= 'product_category'
        verbose_name_plural = 'categories'
        # i dont know wahts happening here



class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, null = True)
    #the category and product have a many to many relationship
    category = models.ForeignKey(ProductCategory, related_name = 'products', on_delete = models.CASCADE, null = True, blank = True)
    ##there should be an autocorrect and option to choose from relevent search options added
    #inventory = models.ForeignKey(Inventory, on_delete = models.SET_NULL) v
    Name = models.CharField(max_length = 200, default = 'write here')
    ProductType = models.CharField(max_length = 200, default = 'write type here, i.e is it a cellphone, radio etc.')
    Price = models.DecimalField(max_digits = 9, decimal_places = 2)
    Stock = models.IntegerField(default = 1)
    image = models.ImageField(upload_to = 'Product_image', blank = True)
    Description = models.TextField(default = 'follow the campus shop guides for creating your description')
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    @property
    #add comment here, why am i doing this
    def LeftOver(self):
        #still need to define this function
        return int(Stock) - 5

    #class Meta:
        #index = (('Name','id'),)
        #Ordering = ('-created',)
        #Product_Ordering = () this is to order by smalles or largest price
        #pass

    def Available(self):
        if self.LeftOver() == 0:
            return False
        else:
            return True

    def __str__(self):
            return self.Name

class Inventory (models.Model):
    #Owner = models.OneToOneField(Shop, on_delete = models.CASCADE)
    #ProductList = Product.product.objects.all()
    pass


class OrderItem(models.Model):
    #on_delete is not a valid keyword argument for ManyToManyField
    product = models.ForeignKey(Product, related_name = 'orders', on_delete = models.CASCADE, null= True)
    #a ForeignKey has to be used abovem istead of ManyToManyField.
    #we us a related_name so that we can be able to track how many orders a particular product has, before completion of order
    #a product is created once, but the quantity can be changed
    #MyCart = models.ForeignKey(ShoppingCartOrder, related_name = 'mycart')
    OrderExists = models.BooleanField(default = False)
    #I think this should be true
    quantity = models.IntegerField(default = 1)
    #auto_now is true, as product is added to the cart
    Date_Added = models.DateTimeField(auto_now_add = True)


    def __str__(self):
        return self.product.Name

class ShoppingCartOrder(models.Model):
    #need to define a remove method
    #need to define an Increase_Quantity method
    #need to define an add_to_cart methodn
    #this model has to be above the OrderItem, and a ForeignKey included in the Orderitem.
    CartOrder = models.ManyToManyField(OrderItem, related_name = 'cartnumbers')
    #change this to
    Owner = models.ForeignKey(Account, on_delete =models.CASCADE, related_name = 'carts')
    #related_name was changed to 'carts'
    #this also has to be changed to a one to one relationship, but the existing cart has to be deleted upon completion of order
    Date_Ordered = models.DateTimeField(auto_now= True)
    # We need to add a boolean conditional that tells us if the cart exists.


    def ReferenceNumber(self):
        date = Date_Ordered.datetime.strftime("%d%m%Y%H%M%S")
        cart_id_string = str(ShoppingCartOrder.id)
        account_str = str(Account.id)
        #creates a unique reference number for the cart when an order is placed
        #or when the function is called.
        #A is used to distinquish the user account number from the reference
        #number
        return account_str + 'A' + cart_id_string + date

    def CartList(self):
        return self.CartOrder.objects.all()

    def TotalCost(self):
        return sum([(item.product.Price)*(item.quantity) for item in self.CartOrder.all()])

    def __str__(self):
        return 'My Cart'

class ProductImage(models.Model):
    image = models.ForeignKey(Product, on_delete = models.CASCADE, null = True, related_name = 'images')
    AddImage = models.ImageField(upload_to = 'Product_image', blank = True)
    name = models.CharField(max_length = 200, default = 'write here')
