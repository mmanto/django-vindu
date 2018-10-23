# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-04 18:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0037_deposito'),
        ('carrito', '0009_auto_20180601_1109'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='deposito_marca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='pedido_deposito_marca', to='mercado_vindu.Deposito'),
        ),
    ]
