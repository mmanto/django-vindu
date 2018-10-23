# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-06-07 19:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0011_auto_20180604_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='iflow_cod_etiqueta',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Código de la etiqueta'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='iflow_print_url',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='URL de la etiqueta'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='iflow_tracking_id',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Tracking Id en Iflow'),
        ),
        migrations.AddField(
            model_name='pedido',
            name='responsable_envio',
            field=models.CharField(choices=[('A', 'Anting'), ('I', 'IFlow')], default='A', max_length=1, verbose_name='Responsable del envio'),
        ),
    ]
