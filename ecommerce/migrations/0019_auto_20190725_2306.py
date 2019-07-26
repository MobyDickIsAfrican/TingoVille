# Generated by Django 2.0.13 on 2019-07-25 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce', '0018_auto_20190723_1425'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='Delivered',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='Sales',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9),
        ),
        migrations.AddField(
            model_name='product',
            name='ToBeDelivered',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='productimage',
            name='Stock',
            field=models.IntegerField(default=1),
        ),
    ]