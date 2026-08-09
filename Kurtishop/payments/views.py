# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import logging
import razorpay
from orders.models import Order
from .models import Payment
from .utils import create_razorpay_order, get_razorpay_client
from orders.utils import send_order_confirmation_email, send_admin_new_order_notification
from django.urls import reverse
from razorpay.errors import SignatureVerificationError
from orders.services import deduct_stock_after_payment, clear_cart_after_payment
from orders.invoice import generate_invoice_pdf

logger = logging.getLogger(__name__)

@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body)
        client = get_razorpay_client()
        params = {
            'razorpay_order_id': data.get('razorpay_order_id'),
            'razorpay_payment_id' : data.get('razorpay_payment_id'),
            'razorpay_signature' : data.get('razorpay_signature'),
        }
        client.utility.verify_payment_signature(params)

        order = get_object_or_404(Order, order_number=data.get('order_number'))

        # Idempotent : already paid -> just return success
        if order.payment_status == Order.PaymentStatus.PAID:
            return JsonResponse({
                'status' : 'success',
                'redirect_url' : reverse('orders:order_success', args=[order.order_number])
            })
        
        order.payment_status = Order.PaymentStatus.PAID
        order.razorpay_payment_id = params['razorpay_payment_id']
        order.order_status = Order.OrderStatus.CONFIRMED
        order.save(update_fields=[
            'payment_status', 'razorpay_payment_id',
            'order_status', 'updated_at'
        ])

        #===== Deduct Stock =====
        deduct_stock_after_payment(order)
        clear_cart_after_order(order)

        payment = Payment.objects.filter(order=order).first()

        if payment:
            payment.razorpay_payment_id = params['razorpay_payment_id']
            payment.razorpay_signature = params['razorpay_signature']
            payment.status = 'success'
            payment.save(update_fields=[
                'razorpay_payment_id', 'razorpay_signature', 'status'
            ])

        if not order.invoice:
            try:
                pdf_file = generate_invoice_pdf(order)
                order.invoice.save(pdf_file.name, pdf_file, save=True)
            except Exception as inv_err:
                logger.exception("Invoice generation failed for %s: %s", order.order_number, inv_err)

        try:
            send_order_confirmation_email(order)
            send_admin_new_order_notification(order)
        except Exception as email_error:
            logger.exception("Email sending failed for %s: %s", order.order_number, email_error)
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': reverse('orders:order_success', args=[order.order_number])
        })
    except SignatureVerificationError:
        return JsonResponse(
            {'status': 'error', 'message': 'Signature verification failed'},
            status=400
        )
    except Exception as e:
        logger.exception("verify_payment failed: %s", e)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def razorpay_webhook(request):
    if request.method != "POST":
        return JsonResponse({'status': 'invalid'}, status=405)

    try:
        payload = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        client = get_razorpay_client()
        client.utility.verify_webhook_signature(
            payload.decode('utf-8'), signature, settings.RAZORPAY_WEBHOOK_SECRET
        )

        event = json.loads(payload)

        if event['event'] == 'payment.captured':
            payment_entity = event['payload']['payment']['entity']
            order = Order.objects.filter(
                razorpay_order_id=payment_entity['order_id']
            ).first()

            if order and order.payment_status != Order.PaymentStatus.PAID:
                order.payment_status = Order.PaymentStatus.PAID
                order.razorpay_payment_id = payment_entity['id']
                order.order_status = Order.OrderStatus.CONFIRMED
                order.save()

                deduct_stock_after_payment(order)

                # Update Payment record
                Payment.objects.filter(order=order).update(
                    razorpay_payment_id=payment_entity['id'],
                    status='success'
                )

                # Generate pdf
                if not order.invoice:
                    try:
                        from orders.invoice import generate_invoice_pdf
                        pdf_file = generate_invoice_pdf(order)
                        order.invoice.save(pdf_file.name, pdf_file, save=True)
                    except Exception as inv_err:
                        logger.exception(
                            "Webhook invoice failed for %s: %s",
                            order.order_number, inv_err
                        )   
                # Send emails (safe to call again)
                send_order_confirmation_email(order)
                send_admin_new_order_notification(order)

        return JsonResponse({'status': 'success'})

    except Exception as e:
        logger.exception("razorpay_webhook failed: %s", e)
        return JsonResponse({'status': 'error'}, status=400)