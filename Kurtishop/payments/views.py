# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order
from .models import Payment
from .utils import create_razorpay_order, get_razorpay_client



@csrf_exempt
def razorpay_webhook(request):
    if request.method == "POST":
        payload = request.body
        signature = request.headers.get('X-Razorpay-Signature')

        try:
            client = get_razorpay_client()  # from utils
            client.utility.verify_webhook_signature(
                payload.decode(), signature, settings.RAZORPAY_WEBHOOK_SECRET
            )

            data = json.loads(payload)
            if data['event'] == 'payment.captured':
                payment_entity = data['payload']['payment']['entity']
                order = Order.objects.filter(razorpay_order_id=payment_entity['order_id']).first()
                if order:
                    order.payment_status = Order.PaymentStatus.PAID
                    order.razorpay_payment_id = payment_entity['id']
                    order.order_status = Order.OrderStatus.CONFIRMED
                    order.save()

                    # Update payment
                    payment = Payment.objects.filter(order=order).first()

                if payment:
                    payment.razorpay_payment_id = payment_entity["id"]
                    payment.razorpay_signature = signature
                    payment.status = 'success'
                    payment.success

            return JsonResponse({'status': 'success'})
        except Exception:
            return JsonResponse({'status': 'error'}, status=400)
    return JsonResponse({'status': 'invalid'}, status=405)