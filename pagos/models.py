from django.db import models

class PagoMercadoPago(models.Model):

    fecha = models.DateTimeField(auto_now_add=True)
    pedido = models.ForeignKey('carrito.Pedido', related_name="pedido_pago_mercadopago")

    http_status = models.IntegerField(blank=True, null=True)
    transaction_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # transaction_details
    external_resource_url = models.CharField(max_length=250, blank=True, null=True)
    payment_method_reference_id = models.CharField(max_length=250, blank=True, null=True)
    financial_institution = models.CharField(max_length=250, blank=True, null=True)
    installment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_received_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    overpaid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    transaction_amount_refunded = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # payer
    payer_first_name = models.CharField(max_length=150, blank=True, null=True)
    payer_last_name = models.CharField(max_length=150, blank=True, null=True)
    payer_entity_type = models.CharField(max_length=150, blank=True, null=True)
    payer_id = models.CharField(max_length=150, blank=True, null=True)
    payer_phone_area_code = models.CharField(max_length=150, blank=True, null=True)
    payer_phone_number = models.CharField(max_length=150, blank=True, null=True)
    payer_phone_extension = models.CharField(max_length=150, blank=True, null=True)
    payer_identification_type = models.CharField(max_length=150, blank=True, null=True)
    payer_identification_number = models.CharField(max_length=150, blank=True, null=True)
    payer_type = models.CharField(max_length=150, blank=True, null=True)
    payer_email = models.CharField(max_length=150, blank=True, null=True)

    currency_id = models.CharField(max_length=150, blank=True, null=True)
    issuer_id = models.CharField(max_length=150, blank=True, null=True)
    statement_descriptor = models.CharField(max_length=150, blank=True, null=True)
    captured = models.NullBooleanField(blank=True)
    date_approved = models.CharField(max_length=150, blank=True, null=True)
    money_release_date = models.CharField(max_length=150, blank=True, null=True)
    notification_url = models.CharField(max_length=150, blank=True, null=True)
    _id = models.CharField(max_length=150, blank=True, null=True)
    collector_id = models.CharField(max_length=150, blank=True, null=True)
    payment_type_id = models.CharField(max_length=150, blank=True, null=True)
    differential_pricing_id = models.IntegerField(blank=True, null=True)
    live_mode = models.NullBooleanField(blank=True)
    payment_method_id = models.CharField(max_length=150, blank=True, null=True)
    status = models.CharField(max_length=150, blank=True, null=True)
    date_last_updated = models.CharField(max_length=50, blank=True, null=True)
    description = models.CharField(max_length=150, blank=True, null=True)
    authorization_code = models.CharField(max_length=150, blank=True, null=True)
    status_detail = models.CharField(max_length=150, blank=True, null=True)
    operation_type = models.CharField(max_length=150, blank=True, null=True)
    coupon_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    binary_mode = models.NullBooleanField(blank=True)

    # card
    card_last_four_digits = models.CharField(max_length=150, blank=True, null=True)
    card_date_last_updated = models.CharField(max_length=150, blank=True, null=True)
    card_expiration_year = models.IntegerField(blank=True, null=True)
    card_expiration_month = models.IntegerField(blank=True, null=True)
    card_cardholder_identification_type = models.CharField(max_length=150, blank=True, null=True)
    card_cardholder_identification_number = models.CharField(max_length=150, blank=True, null=True)
    card_cardholder_name = models.CharField(max_length=150, blank=True, null=True)
    card_date_created = models.CharField(max_length=150, blank=True, null=True)
    card_first_six_digits = models.CharField(max_length=150, blank=True, null=True)
    card_id = models.IntegerField(blank=True, null=True)

    external_reference = models.CharField(max_length=150, blank=True, null=True)
    call_for_authorize_id = models.CharField(max_length=150, blank=True, null=True)
    installments = models.IntegerField(blank=True, null=True)
    date_created = models.CharField(max_length=150, blank=True, null=True)

    # Si es error
    message = models.CharField(max_length=150, blank=True, null=True)

    class Meta:
        verbose_name = "Pago MercadoPago"
        verbose_name_plural = "Pagos MercadoPago"


def guardar_pago_mercadopago(payment_response, http_status, pedido):

    if http_status != 201:
        pago_mercadopago = PagoMercadoPago(
            pedido=pedido,
            http_status=http_status,
            message=payment_response['message']
        )
    else:
        pago_mercadopago = PagoMercadoPago(
            pedido=pedido,
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
            date_created=payment_response['date_created'],
        )
    try:
        pago_mercadopago.save()
    except Exception as e:
        return False, e
    else:
        return True, ''
        '''
        print "------------ Error crear Pago MP ------------------"
        print "Error: ", e
        print "Regalo: ", regalo
        '''
