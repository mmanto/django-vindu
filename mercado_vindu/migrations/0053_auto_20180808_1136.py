# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-08-08 14:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0052_auto_20180807_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producto',
            name='foto_principal_optim',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='images/fotos_productos/optim', verbose_name='Foto Principal Optimizada'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='foto_principal_thumb',
            field=models.ImageField(blank=True, editable=False, null=True, upload_to='images/fotos_productos/thumb', verbose_name='Foto Principal Thumbnail'),
        ),
    ]
