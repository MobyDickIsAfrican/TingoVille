from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from itertools import groupby, dropwhile
from django.contrib.postgres.fields import ArrayField
from django.apps import apps

class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'account')
    # models.CASCADE deletes the account if the User is deleted
    ProcessedOrders = ArrayField(ArrayField(models.IntegerField(blank = True), default = list, blank = True), default = list, blank = True)
    SortedOrders = ArrayField(ArrayField(models.IntegerField(blank = True), default = list, blank = True), default = list, blank = True)
    CancelledOrders = ArrayField(models.CharField(blank = True, max_length = 100), default = list, blank = True)
    email = models.CharField(max_length = 100, unique = True, null = True)
    First_Name = models.CharField(max_length = 50, null = True, blank = False)
    Last_Name = models.CharField(max_length = 60, null = True, blank = False)
    contact = models.CharField(max_length = 11, unique = True, null = True)
    Age = models.IntegerField(default = 21)

    def Message(self, cart_id, order_id):
        self.ProcessedOrders.append([cart_id, order_id])
        return self.save(update_fields = ['ProcessedOrders'])

    def Processed(self):
        unsorted = self.ProcessedOrders
        self.SortedOrders = sorted(self.ProcessedOrders, key = lambda x: x[0])
        return self.save(update_fields = ['SortedOrders'])

    def CheckProcessedFully(self):
        queryset = self.carts.all()
        results = groupby(self.SortedOrders, lambda x: x[0])
        for cart_id, items in results:
            cart = queryset.get(id = cart_id)
            if len(list(items)) == cart.CartOrder.all().count():
                if ProgressBar.objects.filter(cart_id = cart_id).exists():
                    progress_bar = ProgressBar.objects.get(cart_id = cart_id)
                    progress_bar.OrderBeingReadied()
                    self.SortedOrders = list(dropwhile(lambda x: x[0] == cart_id, self.SortedOrders))
                    self.ProcessedOrders = self.SortedOrders

    def __str__(self):
        return self.user.username

    def Declined(self, product_name):
        message = f'Sorry the supplier has cancelled your order for {product_name}'
        return self.CancelledOrders.append(message)





def Create_Account(sender, instance, created, **kwargs):
    if created:
        Account.objects.get_or_create(user = instance)
    #this gets or creates an instance of the the model
#if created - is a boolean that checks if a new object has been created
post_save.connect(Create_Account, sender = User)
# this  saves or updates the Account model when a User is instantiated

class ProgressBar(models.Model):
    account = models.ForeignKey(Account, on_delete = models.CASCADE, related_name = 'progressbars')
    progress = models.IntegerField(default = 1)
    cart_id = models.IntegerField(blank = True)
    completed = models.BooleanField(default = False)

    def OrderBeingReadied(self):
        self.progress = 40
        return self.save(update_fields =['progress'])

    def save(self, *args, **kwargs):
        if self.completed:
            return self.delete()
        else:
            return super(ProgressBar, self).save(*args, **kwargs)
