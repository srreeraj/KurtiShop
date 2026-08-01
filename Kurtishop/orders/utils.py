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

    email = EmailMultiAlternatives(
        subject=f"Order Confirmed – #{order.order_number} | Liara",
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.email],
    )
    email.attach_alternative(html_message, "text/html")

    # Attach PDF invoice
    if order.invoice:
        try:
            # Prefer reading through storage safely
            with order.invoice.open('rb') as f:
                email.attach(
                    filename=f"Invoice_{order.order_number}.pdf",
                    content=f.read(),
                    mimetype="application/pdf",
                )
        except Exception as e:
            print(f"Could not attach invoice PDF: {e}")
            # Optional fallback: generate fresh PDF in memory
            try:
                from .invoice import generate_invoice_pdf
                pdf_file = generate_invoice_pdf(order)
                email.attach(
                    filename=f"Invoice_{order.order_number}.pdf",
                    content=pdf_file.read(),
                    mimetype="application/pdf",
                )
            except Exception as e2:
                print(f"Fallback invoice attach also failed: {e2}")

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

def send_return_request_email(return_request):
    """Notify admin that a customer submitted a return/exchange request"""
    order = return_request.order
    items = return_request.items.select_related("order_item").all()

    context = {
        "return_request": return_request,
        "order": order,
        "items": items,
    }

    try:
        html_message = render_to_string("orders/email/return_request.html", context)
    except Exception:
        html_message = None

    # Build plain text version
    item_lines = []
    for item in items:
        item_lines.append(
            f"- {item.order_item.product_name} "
            f"({item.order_item.color}/{item.order_item.size}) "
            f"× {item.quantity} → {item.get_request_type_display()}"
        )
    items_text = "\n".join(item_lines) if item_lines else "No items"

    plain = (
        f"Customer {order.full_name} ({order.email}) has submitted a "
        f"{return_request.get_request_type_display()} request for order #{order.order_number}.\n\n"
        f"Reason: {return_request.reason}\n\n"
        f"Items:\n{items_text}"
    )

    send_mail(
        subject=f"Return/Exchange Request – #{order.order_number}",
        message=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        html_message=html_message,
        fail_silently=False,
    )


def send_return_decision_email(return_request, approved):
    """Notify customer whether their return/exchange request was approved or rejected"""
    order = return_request.order
    items = return_request.items.select_related("order_item").all()

    context = {
        "return_request": return_request,
        "order": order,
        "items": items,
        "approved": approved,
    }

    try:
        html_message = render_to_string("orders/email/return_decision.html", context)
    except Exception:
        html_message = None

    if approved:
        subject = f"Return/Exchange Approved – #{order.order_number}"
        plain = (
            f"Hi {order.full_name},\n\n"
            f"Your return/exchange request for order #{order.order_number} has been approved.\n"
            f"Our team will contact you shortly with the next steps "
            f"(pickup / shipping instructions).\n\n"
            f"Thank you,\nLiara"
        )
    else:
        subject = f"Return/Exchange Update – #{order.order_number}"
        plain = (
            f"Hi {order.full_name},\n\n"
            f"Unfortunately your return/exchange request for order #{order.order_number} "
            f"could not be approved.\n\n"
            f"{'Admin note: ' + return_request.admin_note if return_request.admin_note else ''}\n\n"
            f"If you have any questions, please reply to this email.\n\n"
            f"Thank you,\nLiara"
        )

    send_mail(
        subject=subject,
        message=plain,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_order_status_update_email(order, old_status=None):
    """Notify customer when order status is updated by admin"""
    context = {
        'order': order,
        'items': order.items.select_related('variant').all(),
        'old_status': old_status,
        'site_url': getattr(settings, 'SITE_URL', 'https://yourdomain.com'),
    }

    try:
        html_message = render_to_string(
            'orders/email/order_status_update.html', context
        )
        plain_message = (
            f"Hi {order.full_name},\n\n"
            f"Your order #{order.order_number} status has been updated to "
            f"{order.get_order_status_display()}.\n\n"
            f"Thank you for shopping with Liara."
        )
    except Exception:
        plain_message = (
            f"Your order #{order.order_number} is now "
            f"{order.get_order_status_display()}."
        )
        html_message = None

    send_mail(
        subject=f"Order Update – #{order.order_number} is now {order.get_order_status_display()}",
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=html_message,
        fail_silently=False,
    )