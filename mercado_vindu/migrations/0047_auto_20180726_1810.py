# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-26 21:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0046_auto_20180726_1805'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='marca',
            name='fecha_ultima_actividad',
        ),
        migrations.AddField(
            model_name='marca',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='marca',
            name='date_updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]