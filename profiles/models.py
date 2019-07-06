from django.db import models
from django.contrib.gis.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime


class Account(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE, related_name = 'account')
# models.CASCADE deletes the account if the User is deleted
    def __str__(self):
        return self.user.username

def Create_Account(sender, instance, created, **kwargs):
    if created:
        Account.objects.get_or_create(user = instance)
        #this gets or creates an instance of the the model
#if created - is a boolean that checks if a new object has been created
post_save.connect(Create_Account, sender = User)
# this  saves or updates the Account model when a User is instantiated
