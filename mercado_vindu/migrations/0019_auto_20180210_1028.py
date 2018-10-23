# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-10 13:28
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mercado_vindu.models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0009_auto_20180205_1923'),
        ('mercado_vindu', '0018_auto_20180209_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='WishList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='producto_wish_list', to='mercado_vindu.Producto')),
            ],
            options={
                'verbose_name_plural': 'Wish Lists',
                'verbose_name': 'Wish List',
            },
        ),
        migrations.AlterField(
            model_name='talleproducto',
            name='talle',
            field=models.CharField(max_length=30, validators=[mercado_vindu.models.validate_talle], verbose_name='Talle'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='talle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='talle_wish_list', to='mercado_vindu.TalleProducto'),
        ),
        migrations.AddField(
            model_name='wishlist',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_wish_list', to='auth_api.UserComprador'),
        ),
        migrations.AlterUniqueTogether(
            name='wishlist',
            unique_together=set([('usuario', 'producto', 'talle')]),
        ),
    ]
