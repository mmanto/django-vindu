# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-21 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0064_auto_20180818_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='marca',
            name='proveedor_pago',
            field=models.CharField(choices=[('MP', 'MercadoPago'), ('PU', 'PayU')], default='MP', max_length=2, verbose_name='Proveedor de pagos'),
        ),
    ]