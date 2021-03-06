# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-15 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0009_auto_20180205_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercomprador',
            name='biografia',
            field=models.TextField(blank=True, max_length=200, null=True, verbose_name='Biografía'),
        ),
        migrations.AddField(
            model_name='usermarca',
            name='foto_avatar',
            field=models.ImageField(blank=True, null=True, upload_to='images/fotos_avatares', verbose_name='Avatar'),
        ),
    ]
