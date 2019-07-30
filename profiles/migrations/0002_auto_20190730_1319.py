# Generated by Django 2.0.13 on 2019-07-30 11:19

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgressBar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('progress', models.IntegerField(default=1)),
                ('cart_id', models.IntegerField(blank=True)),
                ('completed', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='ProcessedOrders',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='account',
            name='SortedOrders',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(blank=True), blank=True, default=list, size=None), blank=True, default=list, size=None),
        ),
        migrations.AddField(
            model_name='progressbar',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='progressbars', to='profiles.Account'),
        ),
    ]
