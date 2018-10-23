# Importaciones Django
from django.conf.urls import url

# Importaciones Propias
from .views import *
from .forms import *

obligaciones_data = {'form_class' : ObligacionesReportForm, 
                     'report_name' : 'Reporte de Obligaciones',
                     'page_template' : 'reports/report_page.html',
                     'pdf_template' : 'reports/obligaciones_report.html',
                     'xls_template' : 'reports/obligaciones_report.html',
                     'report_filename' : 'Reporte_de_Obligaciones'}

urlpatterns = [
    url(r'^obligaciones/$', report_view, obligaciones_data, name='reporte_obligaciones'),
]
