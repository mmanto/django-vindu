# -*- encoding: utf-8 -*-
from django import forms
from django.utils.safestring import mark_safe
from .models import *
from tinymce import TinyMCE

class VoucherAdminForm(forms.ModelForm):

    class Meta:
        model = Voucher
        fields = '__all__'

    def clean(self):
        fecha_vigencia_desde = self.cleaned_data.get('fecha_vigencia_desde')
        fecha_vigencia_hasta = self.cleaned_data.get('fecha_vigencia_hasta')

        if fecha_vigencia_desde > fecha_vigencia_hasta:
            raise forms.ValidationError('La fecha de vigencia DESDE debe ser menor que la fecha HASTA')

        return self.cleaned_data

'''
class VoucherUsadoAdminForm(forms.ModelForm):

    class Meta:
        model = VoucherUsado
        fields = '__all__'
'''

class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False

class TiempoCostoEnvioAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = TiempoCostoEnvio
        fields = '__all__'

class CuotasFormaPagoAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = CuotasFormaPago
        fields = '__all__'

class CambiosYDevolucionesAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = CambiosYDevoluciones
        fields = '__all__'


class AcercaVinduAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = AcercaVindu
        fields = '__all__'


class PoliticasPrivacidadAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = PoliticasPrivacidad
        fields = '__all__'


class FAQAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = FAQ
        fields = '__all__'


class TerminosCondicionesAdminForm(forms.ModelForm):
    text_html = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = TerminosCondiciones
        fields = '__all__'
