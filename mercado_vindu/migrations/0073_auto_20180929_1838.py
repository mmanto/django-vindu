# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-09-29 21:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0072_auto_20180929_1836'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marca',
            name='pu_account_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='PayU Account Id'),
        ),
        migrations.AlterField(
            model_name='marca',
            name='pu_merchand_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='PayU Merchand Id'),
        ),
    ]
