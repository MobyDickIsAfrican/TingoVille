# Generated by Django 2.0.13 on 2019-07-23 12:25

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0017_productcategory_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='AcceptedOrders',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='AcceptedProductIds',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='AcceptedUsersIds',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='PendingOrderIds',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='PendingOrders',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='PendingProductIds',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='shop',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='ecommerce.Shop'),
        ),
    ]