# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-05 16:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0007_auto_20180126_1324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercomprador',
            name='foto_avatar',
            field=models.ImageField(blank=True, null=True, upload_to='images/fotos_avatares', verbose_name='Avatar'),
        ),
    ]