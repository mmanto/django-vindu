# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-13 16:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0012_auto_20180216_1625'),
        ('mercado_vindu', '0043_auto_20180710_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='LikeImagenPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imagen_post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagen_like_imagenpost', to='mercado_vindu.ImagenPost')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_like_imagenpost', to='auth_api.UserComprador')),
            ],
            options={
                'verbose_name': 'Like de Imagen de Post',
                'verbose_name_plural': 'Likes de Imágenes de Posts',
            },
        ),
        migrations.AlterModelOptions(
            name='procesobatch',
            options={'verbose_name': 'Proceso Batch', 'verbose_name_plural': 'Procesos Batch'},
        ),
        migrations.AlterField(
            model_name='procesobatch',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de carga'),
        ),
        migrations.AlterField(
            model_name='procesobatch',
            name='date_updated',
            field=models.DateTimeField(auto_now=True, verbose_name='Ultima fecha de actualización'),
        ),
        migrations.AlterUniqueTogether(
            name='likeimagenpost',
            unique_together=set([('usuario', 'imagen_post')]),
        ),
    ]