# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-17 19:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0006_auto_20180113_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coleccion',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='coleccion_marca', to='mercado_vindu.Marca'),
        ),
        migrations.AlterField(
            model_name='local',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='local_marca', to='mercado_vindu.Marca'),
        ),
        migrations.AlterField(
            model_name='novedad',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='novedad_marca', to='mercado_vindu.Marca'),
        ),
        migrations.AlterField(
            model_name='producto',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='producto_marca', to='mercado_vindu.Marca'),
        ),
    ]
