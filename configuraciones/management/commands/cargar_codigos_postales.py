# -*- encoding: utf-8 -*-
from django.core.management.base import BaseCommand
from configuraciones.models import CodigoPostal, TarifaZonaEnvio, ProvinciaLocalidadZonaTarifa


class Command(BaseCommand):

	def handle(self, *args, **options):
		file = open('codigos_postales.csv','r')
		for line in file:
			list_fields = line.split(',')
			cod_postal = list_fields[1]
			provincia  = list_fields[2]
			municipio  = list_fields[4]
			id_zona    = list_fields[5]
			localidad  = list_fields[6]

			print('cod_postal:', cod_postal)
			print('municipio: ', municipio)
			print('localidad : ', localidad)

			tarifa_zona_obj = TarifaZonaEnvio.objects.get(id_zona=id_zona)

			cod_postal_obj, created = CodigoPostal.objects.get_or_create(cod_postal=cod_postal)

			provincia_zona_tarifa_obj, created = ProvinciaLocalidadZonaTarifa.objects.get_or_create(
				                                                     cod_postal_provincia=cod_postal_obj,
																	 provincia=provincia,
																	 municipio=municipio,
																	 zona_tarifa=tarifa_zona_obj,
																	 localidad=localidad)

