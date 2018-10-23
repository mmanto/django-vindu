import os
import csv
from decimal import Decimal

from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mercado_vindu.models import (
    ARCHIVO_BATCH_TIPOS, ARCHIVO_BATCH_ERROR_TIPOS, Producto, TalleProducto,
    ProcesoBatch, ProcesoBatchError
)


class Command(BaseCommand):
    help = 'Corre los procesos batch cargados en ProcesoBatch'

    def crear_error(self, proceso, linea, linea_nro, error, obj=None):
        campos = {
            'proceso_batch': proceso,
            'linea': ','.join([str(v) for v in linea.values()]),
            'linea_numero': linea_nro+1,
            'error': error,
        }

        if obj:
            campos.update({
                'model_nombre': obj.__class__,
                'model_id': obj.id
            })

        ProcesoBatchError.objects.create(**campos)

    def actualizar_precio(self,eoceso, producto, linea, linea_nro):
        error = False
        precio = linea.get('precio')

        if precio:
            try:
                precio = Decimal(str(precio))
                producto.precio = precio
                producto.save()

            except InvalidOperation:
                error = True
                self.crear_error(
                    proceso, linea, linea_nro,
                    'Precio no es un número decimal', producto)

        else:
            error = True
            self.crear_error(proceso, linea, linea_nro, 'Linea sin precio')

        return error

    def actualizar_porcentaje(self, proceso, producto, linea, linea_nro):
        error = False
        porc_descuento = linea.get('porc_descuento')

        if Decimal(porc_descuento) > 0:
            fecha_desde = linea.get('fecha_descuento_desde')
            fecha_hasta = linea.get('fecha_descuento_hasta')

            if fecha_desde and fecha_hasta:
                try:
                    producto.porc_descuento = Decimal(porc_descuento)
                    producto.fecha_descuento_desde = fecha_desde
                    producto.fecha_descuento_hasta = fecha_hasta
                    producto.save()

                except InvalidOperation:
                    error = True
                    self.crear_error(
                        proceso, linea, linea_nro,
                        'Porcentaje descuento no es un número decimal',
                        producto)

            else:
                error = True
                self.crear_error(
                    proceso, linea, linea_nro,
                    'Porcentaje de descuento sin fecha desde/hasta',
                    producto)
        else:
            if producto.porc_descuento > Decimal('0.00'):
                producto.porc_descuento = Decimal('0.00')
                producto.fecha_descuento_desde = None
                producto.fecha_descuento_hasta = None
                producto.save()

        return error

    def actualizar_producto(self, proceso, reg_id, linea, linea_nro):
        error = False

        try:
            producto = Producto.objects.get(id=reg_id, marca=proceso.marca)

            error_pre = self.actualizar_precio(
                    proceso, producto, linea, linea_nro)

            error_por = self.actualizar_porcentaje(
                    proceso, producto, linea, linea_nro)

            error = error_pre or error_por

        except Producto.DoesNotExist:
            error = True
            self.crear_error(
                proceso, linea, linea_nro, 'Producto inexistente')

        return error

    def actualizar_stock(self, proceso, reg_id, linea, linea_nro):
        error = False
        stock = linea.get('stock')

        if stock:
            try:
                talle_producto = TalleProducto.objects.get(
                    id=reg_id, producto__marca=proceso.marca)

                try:
                    talle_producto.stock = int(stock)
                    talle_producto.save()

                except ValueError:
                    error = True
                    self.crear_error(
                        proceso, linea, linea_nro,
                        'Campo stock no es un entero', talle_producto)

            except TalleProducto.DoesNotExist:
                error = True
                self.crear_error(
                    proceso, linea, linea_nro, 'TalleProducto inexistente')

        else:
            error = True
            self.crear_error(
                proceso, linea, linea_nro, 'Linea sin stock')

        return error

    def handle(self, *args, **options):
        # No se utiliza bulk update ya que no utiliza el metodo save ni llama
        # a los signals que se utilizan en algunos modelos.
        procesos = ProcesoBatch.objects.filter(
            procesado=False, procesado_error=False)

        for proceso in procesos:
            error = False
            error_tipo = None

            try:
                with open(os.path.join(
                        settings.MEDIA_ROOT, proceso.archivo.name)) as fd:
                    archivo_csv = csv.DictReader(fd)
                    _error = None

                    for linea_nro, linea in enumerate(archivo_csv):
                        reg_id = linea.get('id')

                        if reg_id:
                            if proceso.tipo == 'precio':
                                _error = self.actualizar_producto(
                                    proceso, reg_id, linea, linea_nro)

                            elif proceso.tipo == 'stock':
                                _error = self.actualizar_stock(
                                    proceso, reg_id, linea, linea_nro)

                        else:
                            _error = 'No existe el id en la linea'
                            self.crear_error(proceso, linea, linea_nro, _error)

                        if _error:
                            error = True
                            error_tipo = 'registro'

            except IOError:
                error = True
                error_tipo = 'archivo'

            if error:
                proceso.procesado_error = error
                proceso.procesado_error_tipo = error_tipo

                if error_tipo != 'archivo':
                    proceso.procesado = True
                else:
                    proceso.procesado = False
            else:
                proceso.procesado = True

            proceso.procesado_fecha = timezone.now()
            proceso.save()
