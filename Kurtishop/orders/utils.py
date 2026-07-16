from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse


def send_order_confirmation_email(order):
    """Send beautiful confirmation email to customer"""
    context = {
        'order': order,
        'items': order.items.select_related('variant').all(),
        'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'https://yourdomain.com',
    }

    html_message = render_to_string('orders/email/order_confirmation.html', context)
    plain_message = render_to_string('orders/email/order_confirmation.txt', context)

    send_mail(
        subject=f"Order Confirmed - #{order.order_number}",
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )


def send_admin_new_order_notification(order):
    """Notify admin about new order"""
    context = {'order': order}

    html_message = render_to_string('orders/email/admin_new_order.html', context)

    send_mail(
        subject=f"New Order Received - #{order.order_number}",
        message=f"New paid order #{order.order_number} from {order.full_name} (₹{order.grand_total})",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )