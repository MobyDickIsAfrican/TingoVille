# Generated by Django 2.0.13 on 2019-07-28 14:53

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0022_auto_20190725_2325'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='AcceptedObjectId',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='inventory',
            name='PendingObjectId',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None),
        ),
    ]
