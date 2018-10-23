# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-02 21:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0014_auto_20180130_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marcafavorita',
            name='marca',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marca_marca_favorita', to='mercado_vindu.Marca'),
        ),
        migrations.AlterField(
            model_name='marcafavorita',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_marca_favorita', to='auth_api.UserComprador'),
        ),
    ]