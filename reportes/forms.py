# -*- encoding: utf-8 -*-
'''
Forms para generar reportes
'''

from django import forms
from django.template.loader import get_template
from django.template.context import Context, RequestContext
from django.contrib.admin import widgets
from datetime import date

from mercado_vindu.models import Marca
from obligaciones.models import Obligacion

from io import BytesIO
from django.http import HttpResponse
import xhtml2pdf.pisa as pisa


FECHA_INICIAL = date(2018,1,1)

class BaseReportForm(forms.Form):
    
    FORMATO_CHOICES = (('PDF', 'Pdf'), ('XLS', 'Excel'))
    
    formato = forms.ChoiceField(choices=FORMATO_CHOICES)

    
    def _make_context_dict(self):
        """ 
        Returns a dictionary to pass to the report template as the context, 
        should be overriden by subclasses to fill the report data.
        """ 
        
        return {}

    def _render_template(self, request, template_name, format='pdf'):

        template = get_template(template_name)
        context = self._make_context_dict()
        context.update({'format':format, 'fecha': date.today(),
                        'pagesize': 'A4' })
        return template.render(context).encode("UTF-8")
    
    def get_pdf(self, request, template_name):
        """ 
        Returns a pdf object that can be passed in an HttpResponse.
        """
        
        html = self._render_template(request, template_name)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html), response)
        
        '''
        if pdf.err:
            errors = self._errors.setdefault(forms.forms.NON_FIELD_ERRORS, forms.util.ErrorList())
            errors.append("Error en el pdf: %s" % pdf.err)
            
            return None
        
        return result.getvalue()
        '''
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

    
    def get_xls(self, request, template_name):
        """ 
        Returns a xls string that can be passed in an HttpResponse.
        """
        
        return self._render_template(request, template_name, format='xls')

ESTADOS_LIQ_FORM = (
    ('T', 'Todos'),
    ('N', 'No Liquidado'),
    ('L', 'Liquidado'),
)

class ObligacionesReportForm(BaseReportForm):
    marca = forms.ModelChoiceField(queryset=Marca.objects.all().order_by('pk'), empty_label="Todas",
                                required=False)
    desde = forms.DateField(label="Fecha de creación de Obligación desde", widget=widgets.AdminDateWidget(), initial=FECHA_INICIAL)
    hasta = forms.DateField(label="Fecha de creación de Obligación hasta", widget=widgets.AdminDateWidget(), initial=date.today)
    estado_liquidacion = forms.CharField(max_length=1, widget=forms.Select(choices=ESTADOS_LIQ_FORM), required=False)


    def _get_obligaciones(self):      
        marca = self.cleaned_data['marca']
        desde = self.cleaned_data['desde']
        hasta = self.cleaned_data['hasta']
        estado_liquidacion = self.cleaned_data['estado_liquidacion']
        
        qs_obligaciones = Obligacion.objects.all()

        print('1 - qs_obligaciones: ', qs_obligaciones)
        print('2 - marca: ', marca)
        
        if marca:
            qs_obligaciones = qs_obligaciones.filter(pedido__marca=marca)

        print('3 - desde: ', desde)
        
        if desde:
            qs_obligaciones = qs_obligaciones.filter(date_created__date__gte=desde)

        print('3 - hasta: ', hasta)

        if hasta:
            qs_obligaciones = qs_obligaciones.filter(date_created__date__lte=hasta)

        print('4 - estado_liquidacion: ', estado_liquidacion)            
            
        if estado_liquidacion: 
            if estado_liquidacion == 'L':
                qs_obligaciones = qs_obligaciones.filter(estado_liquidacion=True)
                estado_liq_display = 'Liquidado'
            elif estado_liquidacion == 'N':
                qs_obligaciones = qs_obligaciones.filter(estado_liquidacion=False) 
                estado_liq_display = 'No Liquidado'
            else:
                estado_liq_display = 'Todos'
        else:
            estado_liq_display = 'Todos'


        print('5 - qs_obligaciones: ', qs_obligaciones)               

        return qs_obligaciones, estado_liq_display


    def _make_context_dict(self):
        qs_obligaciones, estado_liq_display = self._get_obligaciones()
        
        print('self: ', self)
        context = { 'obligaciones' : qs_obligaciones, 'estado_liq_display': estado_liq_display }
        context.update(self.cleaned_data)
        
        return context
