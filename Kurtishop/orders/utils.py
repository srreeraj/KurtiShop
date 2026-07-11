from django.conf import settings
import razorpay

def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(amount_in_paise):
    client = get_razorpay_client()
    data = {
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    }
    try:
        return client.order.create(data)
    except Exception as e:
        # Log error in production
        print(f"Razorpay Order Creation Error: {e}")
        raise