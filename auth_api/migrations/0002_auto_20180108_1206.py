# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-08 18:06
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Usuario Administrador', 'verbose_name_plural': 'Usuarios Administradores'},
        ),
    ]
