# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-10-11 20:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0026_remove_itemcarrito_precio'),
    ]

    operations = [
        migrations.AddField(
            model_name='carrito',
            name='importe_dto_primera_compra',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, verbose_name='Importe de descuento por primera compra'),
        ),
    ]
