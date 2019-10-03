from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, date
from profiles.models import Account
from django.contrib.postgres.fields import ArrayField
from io import BytesIO
from PIL import Image
from django.core.files import File
import os
from django.urls import reverse
from django.db.models.signals import post_save

def compress(image):
    im = Image.open(image)
    im_io = BytesIO()
    im.save(im_io, 'JPEG', quality = 10)
    new_image = File(im_io, name = image.name)
    return new_image


## creating a shop model for the seller. The AUTH_USER_MODEL is used to link the seller to the user who actually
## created the shop or sold the product.

class Shop(models.Model):
    name = models.ForeignKey(Account, on_delete = models.CASCADE, related_name = 'shop', null = True)
    #each user can have many shops
    Shop_Name = models.CharField(max_length = 30, unique = True)
    Description = models.TextField(max_length = 200)
    #Delivery_ = models.PointField(null=True, blank=True, srid = 4326)
    #srid = 4326 is the defaault and most popular
    Street_Address = models.CharField(max_length = 50, blank = False, default = '1 Jorissen Street')
    Suburb = models.CharField(max_length = 30, blank = False, default = 'Braamforntein')
    City = models.CharField(max_length = 30, blank = False, default = 'Johannesburg')
    ZipCode = models.CharField(max_length = 30, blank =True)
    created = models.DateTimeField(auto_now_add = True, blank = True)
    STORE_CHOICES = (("CASUAL", "Casual Seller"), ("PROFESSIONAL", "Professional"))
    Type = models.CharField(max_length = 50, choices = STORE_CHOICES, null = True)
    image = models.ImageField(upload_to = 'Shop_image', blank = True)
    

    #add cool customiseable stuff for the seller to make shop feel organic.

    # Ask for preferred method of payment
    def __str__(self):
        return str(self.Shop_Name)

    def indexing(self):
        ShopDocument.init()
        doc = ShopDocument(Name = self.Shop_Name, meta = {'id': self.id})
        return doc.save()

    ##def Payment_Options(self)
    ##return None

class ProductCategory (models.Model):
    CategoryName = models.CharField(max_length = 50, unique= True)
    image = models.ImageField(upload_to = 'Category_image', blank = True)

    def __str__(self):
        return self.CategoryName

    class Meta:
        ordering = ['CategoryName']
        #the categories are ordered in alphabetical order
        verbose_name= 'product_category'
        verbose_name_plural = 'categories'
        # i dont know wahts happening here
    def indexing(self):
        doc = CategoryDocument(Name = self.CategoryName, meta = {'id': self.id})
        return doc.save()



class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete = models.CASCADE, null = True)
    #the category and product have a many to many relationship
    category = models.ForeignKey(ProductCategory, related_name = 'products', on_delete = models.CASCADE, null = True)
    ##there should be an autocorrect and option to choose from relevent search options added
    #inventory = models.ForeignKey(Inventory, on_delete = models.SET_NULL) v
    Name = models.CharField(max_length = 200, default = 'write here')
    ProductType = models.CharField(max_length = 200, default = 'write type here, i.e is it a cellphone, radio etc.')
    Price = models.DecimalField(max_digits = 9, decimal_places = 2)
    #Stock = models.IntegerField(default = 1)
    #image = models.ImageField(upload_to = 'Product_image', blank = True)
    #change made here
    Description = models.TextField(default = 'follow the campus shop guides for creating your description')
    Resale = models.BooleanField(default = False)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)

    #class Meta:
        #index = (('Name','id'),)
        #Ordering = ('-created',)
        #Product_Ordering = () this is to order by smalles or largest price
        #pass

    def __str__(self):
            return self.Name

    def indexing(self):
        ProductDocument.init()
        doc = ProductDocument(ProductType = self.ProductType, Name = self.Name, Description = self.Description, meta = {'id' : self.id})
        return doc.save()

class Inventory (models.Model):
    shop = models.OneToOneField(Shop, on_delete= models.CASCADE, related_name = 'inventory', null = True)
    PendingOrders = ArrayField(models.CharField(blank = True, max_length = 255), default = list,  blank = True)
    PendingOrderIds = ArrayField(models.IntegerField(blank = True), default = list,  blank = True)
    PendingProductIds = ArrayField(models.IntegerField(blank = True), default = list,  blank = True)
    PendingObjectId = ArrayField(models.IntegerField(blank = True), default = list,  blank = True)
    AcceptedOrders = ArrayField(models.CharField(blank = True, max_length = 255), default = list,  blank = True)
    AcceptedUsersIds = ArrayField(models.IntegerField(blank = True), default = list,  blank = True)
    AcceptedProductIds = ArrayField(models.IntegerField(blank = True), default = list, blank = True)
    AcceptedObjectId =  ArrayField(models.IntegerField(blank = True), default = list,  blank = True)

    def Messages(self, cart_id, obj_id):
        obj = OrderItem.objects.get(id = obj_id)
        item = obj.product
        product_id = item.id
        name = item.Name
        stock = obj.quantity
        attribute = obj.attribute
        size = obj.size
        Ref = ShoppingCartOrder.objects.get(id = cart_id).ReferenceNumber()
        order_message = f'{name}; {attribute}; {stock}; {size}; {Ref}'
        self.PendingOrders.append(order_message)
        self.PendingProductIds.append(product_id)
        self.PendingOrderIds.append(cart_id)
        self.PendingObjectId.append(obj_id)
        return self.save(update_fields = ['PendingOrders', 'PendingOrderIds', 'PendingProductIds', 'PendingObjectId'])

    def Remove(self, obj_id):
        pending = list(zip(self.PendingOrders, self.PendingOrderIds, self.PendingProductIds, self.PendingObjectId))
        num = 0
        for w, x, y, z in pending:
            if z == obj_id:
                self.PendingOrders.pop(num)
                self.PendingOrderIds.pop(num)
                self.PendingProductIds.pop(num)
                self.PendingObjectId.pop(num)
                return self.save(update_fields = ['PendingOrders', 'PendingOrderIds', 'PendingProductIds', 'PendingObjectId'])
            num += 1

    def Approve(self, obj_id):
        pending = list(zip(self.PendingOrders, self.PendingOrderIds, self.PendingProductIds, self.PendingObjectId))
        num = 0
        for w, x, y, z in pending:
            if z == obj_id:
                message = self.PendingOrders.pop(num)
                cart_id = self.PendingOrderIds.pop(num)
                product_id = self.PendingProductIds.pop(num)
                self.PendingObjectId.pop(num)
                p = Product.objects.get(id = y)
                var = w.split(';')
                string_list = [x.strip() for x in var]
                quantity = int(string_list[2])
                attribute = string_list[1]
                for item in p.images.all():
                    if item.name == attribute:
                        item.ToBeDelivered = item.ToBeDelivered + quantity
                        item.Stock = item.Stock - quantity
                        item.save(update_fields = ['ToBeDelivered', 'Stock'])
                        break
                self.AcceptedOrders.append(message)
                self.AcceptedUsersIds.append(cart_id)
                self.AcceptedProductIds.append(product_id)
                self.AcceptedObjectId.append(obj_id)
                return self.save(update_fields = ['PendingOrders', 'PendingOrderIds', 'PendingProductIds', 'PendingObjectId', 'AcceptedOrders', 'AcceptedUsersIds', 'AcceptedProductIds', 'AcceptedObjectId'])
            num += 1

def Create_Inventory(sender, instance, created, **kwargs):
    if created:
        Inventory.objects.get_or_create(shop = instance)
post_save.connect(Create_Inventory, sender = Shop)


class OrderItem(models.Model):
    #on_delete is not a valid keyword argument for ManyToManyField
    product = models.ForeignKey(Product, related_name = 'orders', on_delete = models.CASCADE, null= True)
    #a ForeignKey has to be used abovem istead of ManyToManyField.
    #we us a related_name so that we can be able to track how many orders a particular product has, before completion of order
    #a product is created once, but the quantity can be changed
    #OrderExists = models.BooleanField(default = False)
    #I think this should be true
    quantity = models.IntegerField(default = 1)
    attribute = models.CharField(default = 'Default', max_length = 200,)
    size = models.CharField(max_length = 100, null = True)
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
    #need to add a description to this model. It will have a default.


    def ReferenceNumber(self):
        date = self.Date_Ordered.strftime("%d%m%Y%H%M%S")
        cart_id_string = str(self.id)
        account_str = str(self.Owner.id)
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
    AddImage = models.ImageField(upload_to = 'Product_image', null = True)
    Stock = models.IntegerField(default = 1)
    name = models.CharField(max_length = 200, default = 'write here')
    ToBeDelivered = models.IntegerField(default = 0)
    #need to manually insert the number of items delivered in django admin
    Delivered = models.IntegerField(default = 0)
    Just_Delivered = models.IntegerField(default = 0)
    Sales = models.DecimalField(default = 0, decimal_places = 2, max_digits = 9)
    sizes = models.CharField(max_length = 100, null = True)
    Returns = models.IntegerField(default = 0)
    Deactivated = models.BooleanField(default = False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        '''this is to delete productimages or products for casual sellers when the stock runs out'''
        if self.Stock == 0:
            pro = self.image
            store = pro.shop
            if store.Type == 'Casual Seller':
                #if there is only one productimage, delete the product
                if self.Deactivated == True:
                    if pro.images.all().count() == 1:
                        return pro.delete()
                    else:
                        return self.delete()
                else:
                    self.ToBeDelivered = self.ToBeDelivered - self.Just_Delivered
                    self.Delivered = self.Delivered + self.Just_Delivered
                    self.Sales = self.image.Price*(self.Delivered)
                    self.Just_Delivered  = 0
                    return super(ProductImage, self).save(*args, **kwargs)
        else:
            self.Delivered = self.Delivered + self.Just_Delivered
            self.Sales = self.image.Price*(self.Delivered)
            self.Just_Delivered  = 0
            return super(ProductImage, self).save(*args, **kwargs)
            
        def delete(self, *args, **kwargs):
            pro = self.image
            if pro.images.all().count() == 1:
                return pro.delete()
            else:
                return super(ProductImage, self).delete(*args, **kwargs)
