# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-27 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0047_auto_20180726_1810'),
    ]

    operations = [
        migrations.AddField(
            model_name='categoria',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='images/categorias', verbose_name='Imagen de la Categoría'),
        ),
    ]
