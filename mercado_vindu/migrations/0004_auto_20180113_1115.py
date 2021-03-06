# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-13 14:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0003_auto_20180110_1501'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tagproducto',
            name='producto',
        ),
        migrations.AlterModelOptions(
            name='fotonovedad',
            options={'verbose_name': 'Imagen de la Novedad', 'verbose_name_plural': 'Imágenes de la Novedad'},
        ),
        migrations.AlterModelOptions(
            name='novedad',
            options={'verbose_name': 'Novedad', 'verbose_name_plural': 'Novedades'},
        ),
        migrations.AddField(
            model_name='producto',
            name='tags',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Tags'),
        ),
        migrations.DeleteModel(
            name='TagProducto',
        ),
    ]
