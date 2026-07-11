import razorpay
from django.conf import settings


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount_in_paise: int):
    client = get_razorpay_client()
    data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    }
    return client.order.create(data)