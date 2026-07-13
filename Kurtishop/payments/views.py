# payments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from orders.models import Order
from .models import Payment
from .utils import create_razorpay_order, get_razorpay_client


def initiate_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    razorpay_order = create_razorpay_order(int(order.grand_total * 100))

    payment, created = Payment.objects.get_or_create(
        order= order,
        defaults={
            "razorpay_order_id": razorpay_order["id"],
            "amount": order.grand_total,
        }
    )

    if not created:
        payment.razorpay_order_id = razorpay_order["id"]
        payment.amount = order.grand_total
        payment.status = "pending"
        payment.save()

    order.razorpay_order_id = razorpay_order['id']
    order.save()

    context = {
        'order': order,
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'razorpay_order_id': razorpay_order['id'],
        'amount': int(order.grand_total * 100),
    }
    return render(request, 'payments/payment_page.html', context)


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