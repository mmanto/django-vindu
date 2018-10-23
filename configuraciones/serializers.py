# -*- encoding: utf-8 -*-
from rest_framework import serializers, exceptions

from .models import *
from django.utils.safestring import mark_safe

class CodigosPostalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = CodigoPostal
        fields = ('cod_postal',) 

 
class ProvinciaLocalidadZonaTarifaSerializer(serializers.ModelSerializer):
    localidad_id = serializers.SerializerMethodField()
    cod_postal   = serializers.SerializerMethodField()

    def get_localidad_id(self, obj):
        return obj.id

    def get_cod_postal(self, obj):
        return obj.cod_postal_provincia.cod_postal

    class Meta:
        model = ProvinciaLocalidadZonaTarifa
        fields = ('localidad_id', 'cod_postal', 'provincia', 'municipio', 'localidad', ) 


def format_html(string):
    string.replace(r"\r\n", r"\n")
    string2 =  "".join(string.splitlines()) 
    return string2.replace('\"', "'")    


class TiempoCostoEnvioSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = TiempoCostoEnvio
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)

class CuotasFormaPagoSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = CuotasFormaPago
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)

class CambiosDevolucionesSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = CambiosYDevoluciones
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)


class AcercaVinduSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = AcercaVindu
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)


class PoliticasPrivacidadSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = PoliticasPrivacidad
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)


class FAQSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = FAQ
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)

class TerminosCondicionesSerializer(serializers.ModelSerializer):
    text_html = serializers.SerializerMethodField()

    class Meta:
        model = TerminosCondiciones
        fields = ('text_html',)

    def get_text_html(self, obj):
        return format_html(obj.text_html)