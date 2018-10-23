from django.shortcuts import render
import mercadopago
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import datetime

from carrito.models import Pedido, LineaPedido 
import threading
import mercadopago
import requests
from .models import PagoMercadoPago
from vindu.emails_manager import enviar_mails_aviso_compra


def grabar_pago_MP(payment_response, http_status, pedido_obj):
    pago_mercadopago = PagoMercadoPago(
        pedido=pedido_obj,
        http_status=http_status,
        transaction_amount=payment_response['transaction_amount'],

        external_resource_url=payment_response['transaction_details']['external_resource_url'],
        payment_method_reference_id=payment_response['transaction_details']['payment_method_reference_id'],
        financial_institution=payment_response['transaction_details']['financial_institution'],
        installment_amount=payment_response['transaction_details']['installment_amount'],
        net_received_amount=payment_response['transaction_details']['net_received_amount'],
        total_paid_amount=payment_response['transaction_details']['total_paid_amount'],
        overpaid_amount=payment_response['transaction_details']['overpaid_amount'],

        transaction_amount_refunded=payment_response['transaction_amount_refunded'],

        payer_first_name=payment_response['payer']['first_name'],
        payer_last_name=payment_response['payer']['last_name'],
        payer_entity_type=payment_response['payer']['entity_type'],
        payer_id=payment_response['payer']['id'],
        payer_phone_area_code=payment_response['payer']['phone']['area_code'],
        payer_phone_number=payment_response['payer']['phone']['number'],
        payer_phone_extension=payment_response['payer']['phone']['extension'],
        payer_identification_type=payment_response['payer']['identification']['type'],
        payer_identification_number=payment_response['payer']['identification']['number'],
        payer_type=payment_response['payer']['type'],
        payer_email=payment_response['payer']['email'],

        currency_id=payment_response['currency_id'],
        issuer_id=payment_response['issuer_id'],
        statement_descriptor=payment_response['statement_descriptor'],
        captured=payment_response['captured'],
        date_approved=payment_response['date_approved'],
        notification_url=payment_response['notification_url'],
        _id=str(payment_response['id']),
        collector_id=str(payment_response['collector_id']),
        payment_type_id=payment_response['payment_type_id'],
        differential_pricing_id=payment_response['differential_pricing_id'],
        live_mode=payment_response['live_mode'],
        payment_method_id=payment_response['payment_method_id'],
        status=payment_response['status'],
        date_last_updated=payment_response['date_last_updated'],
        description=payment_response['description'],
        authorization_code=payment_response['authorization_code'],
        status_detail=payment_response['status_detail'],
        operation_type=payment_response['operation_type'],
        coupon_amount=payment_response['coupon_amount'],
        binary_mode=payment_response['binary_mode'],

        card_last_four_digits=payment_response['card']['last_four_digits'],
        card_date_last_updated=payment_response['card']['date_last_updated'],
        card_expiration_year=payment_response['card']['expiration_year'],
        card_expiration_month=payment_response['card']['expiration_month'],
        card_cardholder_identification_type=payment_response['card']['cardholder']['identification']['type'],
        card_cardholder_identification_number=payment_response['card']['cardholder']['identification']['number'],
        card_cardholder_name=payment_response['card']['cardholder']['name'],
        card_date_created=payment_response['card']['date_created'],
        card_first_six_digits=payment_response['card']['first_six_digits'],
        card_id=payment_response['card']['id'],

        external_reference=payment_response['external_reference'],
        call_for_authorize_id=payment_response['call_for_authorize_id'],
        installments=payment_response['installments'],
        date_created=payment_response['date_created']
        )
    try:
        pago_mercadopago.save()
    except Exception as e:
        return False, e, None
    else:
        return True, '', pago_mercadopago 


class GetDetallesPago(threading.Thread):
    def __init__(self, request, pago_id, pedido_obj):
        threading.Thread.__init__(self)
        self.request = request
        self.pago_id = pago_id
        self.pedido_obj = pedido_obj

    def get_payment_method(self, pago_obj, payment_methods_info):
        payment_type = ''
        payment_method = ''

        payment_method_id = pago_obj.payment_method_id
        for payment in payment_methods_info:
            if payment['id'] == payment_method_id:
                payment_method  = payment['name']
                payment_type_id = payment['payment_type_id']
                break

        if payment_type_id == 'credit_card':
            payment_method = 'Tarjeta de Crédito'
        elif payment_type_id == 'ticket':
            payment_method = 'Ticket'
        elif payment_type_id == 'debit_card':
            payment_method = 'Tarjeta de Débito'
        elif payment_type_id == 'atm':
            payment_method = 'ATM' 
        elif payment_type_id == 'prepaid_card':
            payment_method = 'Tarjeta Prepaga'

        return payment_type, payment_method

    def run(self):
            # Autenticación en MP con las credenciales del seller
            marca = self.pedido_obj.marca
            try:
                mp = mercadopago.MP(marca.mp_client_id, marca.mp_client_secret)  # seller credentials
            except:
                return ({"error": "error en credenciales del vendedor"}) 

            try:
                access_token = mp.get_access_token()
            except:
                return ({"error": "error en credenciales del vendedor"}) 


            payments_mp_url = 'https://api.mercadopago.com/v1/payments/'
            payments_mp_url += str(self.pago_id)
            payments_mp_url += '?access_token='
            payments_mp_url += access_token
            response = requests.get(payments_mp_url)
            http_status = response.status_code
            payment_info = response.json()
            print('payment_info: ', payment_info)
            # Se graba la tabla de Pagos

            flag_grabar_pago, mensaje, pago_obj = grabar_pago_MP(payment_info, http_status, self.pedido_obj)

            if not flag_grabar_pago:
                print('error al grabar pago de MP, error: ', mensaje)

            # Se envían mails por la compra hecha: al comprador, a la marca y a Vindu
            if http_status == 200 and flag_grabar_pago:
                payment_methods_mp_url = 'https://api.mercadopago.com/v1/payment_methods'
                payment_methods_mp_url += '?access_token='
                payment_methods_mp_url += access_token
                response = requests.get(payment_methods_mp_url)
                http_status = response.status_code
                payment_methods_info = response.json()
                print('payment_methods_info: ', payment_methods_info)

                payment_type, payment_method = self.get_payment_method(pago_obj, payment_methods_info)

                enviar_mails_aviso_compra(self.request, pago_obj, payment_type, payment_method)


class ActualizarStocks(threading.Thread):
    def __init__(self, pedido_obj):
        threading.Thread.__init__(self)
        self.pedido_obj = pedido_obj

    def run(self):
        qs_lineas_pedido = LineaPedido.objects.filter(pedido=self.pedido_obj)
        for linea_pedido in qs_lineas_pedido:
            articulo_obj = linea_pedido.articulo
            print('articulo_obj.stock: ', articulo_obj.stock)
            print('linea_pedido.cantidad: ', linea_pedido.cantidad)
            articulo_obj.stock -= linea_pedido.cantidad
            if articulo_obj.stock < 0: 
                articulo_obj.stock = 0
            print('articulo_obj.stock actualizado: ', articulo_obj.stock)
            articulo_obj.save()

@csrf_exempt
def ipn_argentina(request, external_reference):

    print('entra a ipn_argentina')
    print('request.GET: ', request.GET)
    print('external_reference: ', external_reference)

    if "id" in request.GET:
        external_reference = int(external_reference)
        topic = request.GET['topic']

        if topic == 'payment':
            try:
                pedido_obj = Pedido.objects.get(pk=external_reference)
            except:
                pass
            else:
                marca = pedido_obj.marca
                mp = mercadopago.MP(marca.mp_client_id, marca.mp_client_secret)
                pago = mp.get_payment_info(request.GET['id'])
                # Posibles respuestas:
                print('pago: ', pago)
                print('status del pago: ', pago['status'])
                print('estado del pago: ', pago['response']['collection']['status'])
                print('nro de pedido: ', pago['response']['collection']['external_reference'])
                if pago['status'] == 200 and pago['response']['collection']['status'] == 'approved':
                    # Acá se evita que MP mande dos o más veces la notificación
                    # Si ya existe el pago en la tabla de Pagos,se by-passea esta seccion:
                    if not PagoMercadoPago.objects.filter(pedido=pedido_obj).exists():
                        # Acá hay que actualizar el Pedido con los datos y el estado del pago
                        pedido_obj.estado_pedido = 'P'  # Pendiente de entrega
                        pedido_obj.fecha_pago  = datetime.date.today()
                        pedido_obj.comprobante_mercadopago = pago['response']['collection']['id']
                        pedido_obj.save()

                        # Continúa el procesamiento por medio de threads
                        # 1er Thread) Consulta detalles del pago, los guarda en tabla y envía mails de aviso
                        pago_id = pago['response']['collection']['id']
                        thread1 = GetDetallesPago(request, pago_id, pedido_obj)
                        thread1.start()

                        # 2do Thread) Actualiza stocks
                        thread2 = ActualizarStocks(pedido_obj)
                        thread2.start()

                        # 3er Thread) Crea entradas en la tabla de Obligaciones

                
    return HttpResponse(status=200)

@csrf_exempt
def mp_pago_exitoso(request):
    context = {}
    pedido_pk = request.GET.get('p', None)
    #transaction_amount = request.GET.get('a', None)
    #statement_descriptor = request.GET.get('s', None)

    statement_descriptor = 'WWW.MERCADOPAGO.COM'

    if pedido_pk:
        try:
            pedido_obj = Pedido.objects.get(pk=pedido_pk)
        except:
            pass
        else:
            context['pedido'] = pedido_obj
            transaction_amount = pedido_obj.importe_total
            context['statement_descriptor'] = statement_descriptor
            context['transaction_amount'] = transaction_amount
    return render(request, 'pagos/mp_pago_exitoso.html', context)


def prueba_mail_html(request):
    pago_obj   = PagoMercadoPago.objects.get(pk=1)

    payment_type = 'Tarjeta de Crédito'
    payment_method = 'Visa'

    return enviar_mails_aviso_compra(request, pago_obj, payment_type, payment_method)
