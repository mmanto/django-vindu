# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-14 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0020_auto_20180214_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marca',
            name='descripcion',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Descripción'),
        ),
        migrations.AlterField(
            model_name='marca',
            name='sitio_web',
            field=models.URLField(blank=True, null=True, verbose_name='Sitio web'),
        ),
    ]
