# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-23 17:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0044_auto_20180713_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='marca',
            name='pu_client_id',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Mercado Pago Client Id'),
        ),
        migrations.AddField(
            model_name='marca',
            name='pu_client_secret',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Mercado Pago Client Secret'),
        ),
        migrations.AddField(
            model_name='marca',
            name='terminos',
            field=models.BooleanField(default=False, verbose_name='Acepto los términos y condiciones de uso'),
        ),
        migrations.AlterField(
            model_name='marca',
            name='telefono_contacto',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Teléfono contacto ventas'),
        ),
    ]
