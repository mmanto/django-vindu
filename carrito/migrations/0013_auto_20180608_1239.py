# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-08 15:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0012_auto_20180607_1604'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='cargo_costo_envio',
            field=models.CharField(choices=[('A', 'Costo de envío a cargo de Anting'), ('M', 'Costo de envío a cargo de la Marca')], default='A', max_length=1, verbose_name='Cargo costo del envio'),
        ),
    ]