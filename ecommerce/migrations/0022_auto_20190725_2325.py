# Generated by Django 2.0.13 on 2019-07-25 21:25

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0021_auto_20190725_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='PendingOrderIds',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
    ]