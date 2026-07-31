from django.core.mail import EmailMultiAlternatives, send_mail
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

    try:
        html_message = render_to_string('orders/email/order_confirmation.html', context)
        plain_message = render_to_string('orders/email/order_confirmation.txt', context)
    except Exception as template_error:
        plain_message = f"Your order #{order.order_number} has been confirmed. Total: ₹{order.grand_total}"
        html_message = f"<h2>Order #{order.order_number} Confirmed</h2><p>Total: ₹{order.grand_total}</p>"

    mail = EmailMultiAlternatives(
        subject=f"Order Confirmed – #{order.order_number} | Liara",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.attach_alternative(html_message, "text/html")

    # Attach the PDF invoice if it exists
    if order.invoice:
        try:
            order.invoice.open('rb')
            email.attach(
                filename=f"Invoice_{order.order_number}.pdf",
                content=order.invoice.read(),
                mimetype="application/pdf",
            )
            order.invoice.close()
        except Exception as e:
            print(f"Could not attach invoice PDF: {e}")

    email.send(fail_silently=False)

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

def send_cancellation_request_email(order):
    """Notify admin that a customer requested cancellation"""
    context = {'order': order}

    html_message = render_to_string('orders/email/cancellation_request.html', context)

    send_mail(
        subject=f"Cancellation Requested - #{order.order_number}",
        message=(
            f"Customer {order.full_name} ({order.email}) has requested cancellation "
            f"for order #{order.order_number}.\nReason: {order.cancellation_reason}"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )


def send_cancellation_decision_email(order, approved):
    """Notify customer whether their cancellation request was approved or rejected"""
    context = {'order': order, 'approved': approved}

    html_message = render_to_string('orders/email/cancellation_decision.html', context)
    subject = (
        f"Order Cancelled - #{order.order_number}" if approved
        else f"Cancellation Request Update - #{order.order_number}"
    )
    plain = (
        f"Your order #{order.order_number} has been cancelled."
        if approved else
        f"Your cancellation request for order #{order.order_number} was not approved. "
        f"Your order is being processed as normal."
    )

    send_mail(
        subject=subject,
        message=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )