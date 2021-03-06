# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-16 01:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0010_auto_20180215_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercomprador',
            name='notif_marcas',
            field=models.BooleanField(default=True, verbose_name='Recibir notificaciones de marcas seguidas'),
        ),
        migrations.AddField(
            model_name='usercomprador',
            name='notif_vindu',
            field=models.BooleanField(default=True, verbose_name='Recibir notificaciones de Vindu'),
        ),
        migrations.AddField(
            model_name='usercomprador',
            name='wishlist_visible',
            field=models.BooleanField(default=True, verbose_name='WishList visible'),
        ),
    ]
