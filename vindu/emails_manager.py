# -*- encoding: utf-8 -*-
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
#from django.template import Context
from django.core import mail
from .settings import DEFAULT_FROM_EMAIL
from django.utils.html import strip_tags


# Envía mail de registración 
def enviar_signup_mail(request, user):

    html = get_template("signup.html")

    content = {'user': user}
    html_content = html.render(content)
    text_content = strip_tags(html_content)
    asunto = 'Registración en Aplicación Vindu'
    remitente = DEFAULT_FROM_EMAIL

    emails_list = []

    destinatario = user.email
    msg = EmailMultiAlternatives(asunto, text_content, remitente, [destinatario])
    msg.attach_alternative(html_content, "text/html")
    emails_list.append(msg)

    try:
        # Manually open the connection
        connection = mail.get_connection()
    except:
        pass
    else:
        # Send all emails in a single call 
        connection.send_messages(emails_list)
        ############################################################################
        # The connection was already opened so send_messages() doesn't close it.
        # We need to manually close the connection.
        connection.close()

# Envía mail de reseteo de password
def enviar_reset_psw_mail(request, user, content):

    html = get_template("registration/password_reset_email.html")
    subject = 'Recupero de contraseña'

    html_content = html.render(content)
    text_content = strip_tags(html_content)
    from_email = DEFAULT_FROM_EMAIL

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")

    emails_list = [msg]

    try:
        # Manually open the connection
        connection = mail.get_connection()
    except:
        pass
    else:
        # Send all emails in a single call 
        connection.send_messages(emails_list)
        ############################################################################
        # The connection was already opened so send_messages() doesn't close it.
        # We need to manually close the connection.
        connection.close()


# Envía mails de aviso de compra al comprador, a Vindu y a la marca 
def enviar_mails_aviso_compra(request, pago_obj, payment_type, payment_method):
    from carrito.models import LineaPedido
    pedido_obj = pago_obj.pedido
    qs_lineas_pedido = LineaPedido.objects.filter(pedido=pedido_obj)

    html = get_template("aviso_compra_comprador.html")
    content = {'request': request, 'pedido': pedido_obj, 'pago': pago_obj, 'lineas_pedido': qs_lineas_pedido,
               'payment_type': payment_type, 'payment_method': payment_method}
    html_content = html.render(content)


    '''
    # Esta parte es para probar el HTML por pantalla
    from django.http import HttpResponse

    return HttpResponse(html_content)
    ## HASTA ACA
    '''

    email_comprador = pedido_obj.usuario_comprador.email
    text_content = strip_tags(html_content)
    from_email = DEFAULT_FROM_EMAIL

    subject = 'Confirmación de compra en Vindu'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [email_comprador])
    msg.attach_alternative(html_content, "text/html")

    emails_list = [msg]

    try:
        # Manually open the connection
        connection = mail.get_connection()
    except:
        pass
    else:
        # Send all emails in a single call 
        connection.send_messages(emails_list)
        ############################################################################
        # The connection was already opened so send_messages() doesn't close it.
        # We need to manually close the connection.
        connection.close()