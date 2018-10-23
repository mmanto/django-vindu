# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-03-06 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mercado_vindu', '0029_auto_20180306_0031'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcercaVindu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Acerca de Vindu',
                'verbose_name_plural': 'Acerca de Vindu',
            },
        ),
        migrations.CreateModel(
            name='CambiosYDevoluciones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Cambios y Devoluciones',
                'verbose_name_plural': 'Cambios y Devoluciones',
            },
        ),
        migrations.CreateModel(
            name='ClaseMarca',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True, verbose_name='Descripción')),
            ],
            options={
                'verbose_name': 'Clase de Marca',
                'verbose_name_plural': 'Clases de Marca',
            },
        ),
        migrations.CreateModel(
            name='CuotasFormaPago',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Cuotas y Formas de Pago',
                'verbose_name_plural': 'Cuotas y Formas de Pago',
            },
        ),
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'FAQ',
                'verbose_name_plural': 'FAQ',
            },
        ),
        migrations.CreateModel(
            name='PoliticasPrivacidad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Políticas de Privacidad',
                'verbose_name_plural': 'Políticas de Privacidad',
            },
        ),
        migrations.CreateModel(
            name='TerminosCondiciones',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Términos y Condiciones',
                'verbose_name_plural': 'Términos y Condiciones',
            },
        ),
        migrations.CreateModel(
            name='TiempoCostoEnvio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_html', models.TextField(verbose_name='Texto HTML')),
            ],
            options={
                'verbose_name': 'Tiempo y Costo de Envío',
                'verbose_name_plural': 'Tiempos y Costos de Envío',
            },
        ),
        migrations.AddField(
            model_name='categoria',
            name='tabla_talles',
            field=models.ImageField(blank=True, null=True, upload_to='', verbose_name='Tabla de Talles'),
        ),
        migrations.AddField(
            model_name='marca',
            name='clase_marca',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='mercado_vindu.ClaseMarca'),
        ),
    ]