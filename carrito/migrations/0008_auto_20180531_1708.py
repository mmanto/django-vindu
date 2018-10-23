# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-05-31 20:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('carrito', '0007_pedido_voucher_aplicado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Descuento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo_descuento', models.CharField(max_length=25, verbose_name='Motivo del descuento')),
                ('importe_descuento', models.DecimalField(decimal_places=2, max_digits=15, verbose_name='Importe del descuento')),
            ],
            options={
                'verbose_name': 'Descuento',
                'verbose_name_plural': 'Descuentos',
            },
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='estado_pago',
        ),
        migrations.AlterField(
            model_name='pedido',
            name='estado_pedido',
            field=models.CharField(choices=[('I', 'Pendiente de pago'), ('P', 'Pendiente de entrega'), ('E', 'Entregado'), ('C', 'Cancelado'), ('E', 'Devuelto')], default='P', max_length=1, verbose_name='Estado del Pedido'),
        ),
        migrations.AddField(
            model_name='descuento',
            name='pedido',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descuento_pedido', to='carrito.Pedido'),
        ),
    ]
