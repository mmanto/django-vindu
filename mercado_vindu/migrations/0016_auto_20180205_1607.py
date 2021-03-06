# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-05 19:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth_api', '0008_auto_20180205_1319'),
        ('mercado_vindu', '0015_auto_20180202_1843'),
    ]

    operations = [
        migrations.CreateModel(
            name='MarcaSeguida',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marca', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marca_marca_seguida', to='mercado_vindu.Marca')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usuario_marca_seguida', to='auth_api.UserComprador')),
            ],
            options={
                'verbose_name': 'Marca Seguida',
                'verbose_name_plural': 'Marcas Seguidas',
            },
        ),
        migrations.AlterUniqueTogether(
            name='marcafavorita',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='marcafavorita',
            name='marca',
        ),
        migrations.RemoveField(
            model_name='marcafavorita',
            name='usuario',
        ),
        migrations.DeleteModel(
            name='MarcaFavorita',
        ),
        migrations.AlterUniqueTogether(
            name='marcaseguida',
            unique_together=set([('usuario', 'marca')]),
        ),
    ]
