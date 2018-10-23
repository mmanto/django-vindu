# -*- coding: utf-8 -*-

from django.template import RequestContext
from django.shortcuts import render
from django import http
import datetime


def make_response(content, filename, extension='pdf', mimetype='application/pdf'):
    """
    Takes a pdf form output and returns the HttpResponse for the attachment,
    with the given filename and the current datetime.
    """
    
    response = http.HttpResponse(content)
                
    filename += datetime.datetime.now().strftime('-%d-%m-%y-%H-%M-%S')
    response['Content-Disposition'] = 'attachment; filename=%s.%s' % (
                                                        filename, extension)
                    
    return response

def report_view(request, form_class, report_name, page_template, 
                pdf_template, xls_template, report_filename):
    
    if request.method == 'POST':
        #print 'entra a form_class POST'
        form = form_class(request.POST)
        if form.is_valid():
            
            if form.cleaned_data['formato'] == 'PDF':
                result = form.get_pdf(request, pdf_template)
            
                if result: #errores en pdf         
                    return make_response(result, report_filename)
            
            else:
                result = form.get_xls(request, xls_template)
                return make_response(result, report_filename, 'xls', 
                                     'text/xls')
    
    else:
        print('entra a form_class no POST')
        print('entra a forms_class(request)')
        print('page_template: ' , page_template)
        print('form_class: ', form_class)

        form = form_class()

        
    print('form: ' , form)
    
    return render(request, page_template, context={'title':report_name, 'form':form })

