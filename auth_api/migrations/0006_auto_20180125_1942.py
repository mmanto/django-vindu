# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-25 22:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('socialaccount', '0003_extra_data_default_dict'),
        ('account', '0002_email_max_length'),
        ('admin', '0002_logentry_remove_auto_add'),
        ('authtoken', '0002_auto_20160226_1747'),
        ('auth_api', '0005_auto_20180125_1527'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useradmin',
            name='marca',
        ),
        migrations.RemoveField(
            model_name='useradmin',
            name='user_ptr',
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'Usuario Administrador', 'verbose_name_plural': 'Usuarios Administradores'},
        ),
        migrations.DeleteModel(
            name='UserAdmin',
        ),
    ]
