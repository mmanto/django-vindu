# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-09-29 21:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0022_pedido_url_pago_mp'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='proveedor_pago',
            field=models.CharField(choices=[('MP', 'MercadoPago'), ('PU', 'PayU')], default='MP', max_length=2, verbose_name='Proveedor de pagos'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='url_pago_PU',
            field=models.URLField(blank=True, null=True, verbose_name='Init point PU'),
        ),
    ]
