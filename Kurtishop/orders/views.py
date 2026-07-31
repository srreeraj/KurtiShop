from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404
from .invoice import generate_invoice_pdf
from cart.models import Cart
from .models import Order, OrderStatusHistory, ReturnRequest, ReturnRequestItem
from .forms import OrderForm, OrderLookupForm, OrderCancellationForm, ReturnLookupForm, ReturnRequestForm
from .services import create_order_from_cart
from payments.utils import create_razorpay_order
from django.conf import settings
from payments.models import Payment
from .utils import send_cancellation_request_email
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.db import transaction

# Create your views here.

def checkout(request):
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    cart = get_object_or_404(Cart, session_key=session_key)

    if not cart.items.exists():
        return redirect('cart:cart_drawer')

    # Calculate values for order summary
    items = cart.items.select_related(
        'variant__product',
        'variant__color',
        'variant__size'
    ).all()

    subtotal = sum(item.total_price for item in items)                    # Discounted subtotal
    subtotal_original = sum(
        item.variant.price * item.quantity for item in items
    )
    total_discount = subtotal_original - subtotal

    shipping = 0
    tax = 0
    grand_total = subtotal + shipping + tax - 0  # discount already subtracted above

    context = {
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'subtotal_original' : subtotal_original,
        'total_discount' : total_discount,
        'discount': total_discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'show_button': True,
        'button_text': 'Proceed to Secure Payment',
    }

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = form.cleaned_data
            subtotal = sum(item.total_price for item in cart.items.all())

            order = create_order_from_cart(cart, {
                **order_data,
                'subtotal': subtotal,
                'total_discount': total_discount,
                'discount': total_discount,
                'shipping_charge': shipping,
                'tax': tax,
                'grand_total': grand_total,
                'payment_method': 'online',
            })
            razorpay_order = create_razorpay_order(int(order.grand_total * 100))

            payment, created = Payment.objects.get_or_create(
                order=order,
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

            context.update({
                'form': form,
                'order': order,
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'razorpay_order_id': razorpay_order['id'],
                'amount': int(order.grand_total * 100),
                'trigger_payment': True,   # tells the template to auto-open Razorpay
                # Extra context for success/failure pages if needed
                'total_discount': total_discount,
                'subtotal_original': subtotal_original,
                'breadcrumbs': [
                    {'name': 'Checkout'},
                ],
            })
            return render(request, 'orders/checkout.html', context)
    else:
        form = OrderForm()

    context['form'] = form
    return render(request, 'orders/checkout.html', context)


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_detail.html', {'order': order})


def order_lookup(request):
    """Guest enters Order Number + Email to find their order."""
    order = None
    searched = False

    if request.method == "POST":
        form = OrderLookupForm(request.POST)
        if form.is_valid():
            searched = True
            order_number = form.cleaned_data["order_number"]
            email = form.cleaned_data["email"]
            order = Order.objects.filter(
                order_number=order_number,
                email__iexact=email,
            ).first()

            if order:
                return redirect('orders:order_cancel_detail', order_number=order.order_number)
            else:
                messages.error(
                    request,
                    "We couldn't find an order matching that Order Number and Email. "
                    "Please check the details and try again."
                )
    else:
        form = OrderLookupForm()

    return render(request, 'orders/order_lookup.html', {
        'form': form,
        'searched': searched,
    })


def order_cancel_detail(request, order_number):
    """Show order status + cancellation option, guarded by email re-verification."""
    order = get_object_or_404(Order, order_number=order_number)
    cancel_form = OrderCancellationForm(initial={
        'order_number': order.order_number,
    })

    context = {
        'order': order,
        'items': order.items.select_related('variant__product', 'variant__color', 'variant__size'),
        'is_cancellable': order.is_cancellable(),
        'cancellation_deadline': order.cancellation_deadline(),
        'cancel_form': cancel_form,
    }
    return render(request, 'orders/order_cancel_detail.html', context)


def request_cancellation(request, order_number):
    """Handle the POST submission of a cancellation request."""
    if request.method != "POST":
        return redirect('orders:order_lookup')

    order = get_object_or_404(Order, order_number=order_number)
    form = OrderCancellationForm(request.POST)

    # Re-verify identity via email submitted in the hidden field
    submitted_email = request.POST.get("email", "").strip().lower()
    if submitted_email != order.email.lower():
        messages.error(request, "Verification failed. Please look up your order again.")
        return redirect('orders:order_lookup')

    if not order.is_cancellable():
        messages.error(request, "This order is no longer eligible for cancellation.")
        return redirect('orders:order_cancel_detail', order_number=order.order_number)

    if form.is_valid():
        reason = form.cleaned_data["reason"]

        with transaction.atomic():
            order.cancellation_reason = reason
            order.order_status = Order.OrderStatus.CANCELLATION_REQUESTED
            order.save(update_fields=["cancellation_reason", "order_status", "updated_at"])

            OrderStatusHistory.objects.create(
                order=order,
                status=Order.OrderStatus.CANCELLATION_REQUESTED,
                note=f"Customer requested cancellation: {reason}",
            )

        send_cancellation_request_email(order)

        messages.success(
            request,
            "Your cancellation request has been submitted. Our team will review it shortly."
        )
        return redirect('orders:order_cancel_detail', order_number=order.order_number)

    messages.error(request, "Please provide a reason for cancellation.")
    return redirect('orders:order_cancel_detail', order_number=order.order_number)

def download_invoice(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    # Always regenerate if missing or if the stored file is broken
    try:
        if not order.invoice or not order.invoice.storage.exists(order.invoice.name):
            pdf_file = generate_invoice_pdf(order)
            order.invoice.save(pdf_file.name, pdf_file, save=True)
    except Exception as e:
        print(f"Invoice generation failed: {e}")
        # Fallback: generate in memory and serve directly
        pdf_file = generate_invoice_pdf(order)
        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename=f"Invoice_{order.order_number}.pdf",
            content_type="application/pdf",
        )

    return FileResponse(
        order.invoice.open("rb"),
        as_attachment=True,
        filename=f"Invoice_{order.order_number}.pdf",
        content_type="application/pdf",
    )

def return_lookup(request):
    """Guest enters Order Number + Email to start a return/exchange."""
    if request.method == "POST":
        form = ReturnLookupForm(request.POST)
        if form.is_valid():
            order_number = form.cleaned_data["order_number"]
            email = form.cleaned_data["email"]

            order = Order.objects.filter(
                order_number=order_number,
                email__iexact=email,
            ).first()

            if order:
                return redirect("orders:return_detail", order_number=order.order_number)
            else:
                messages.error(
                    request,
                    "We couldn't find an order matching that Order Number and Email."
                )
    else:
        form = ReturnLookupForm()

    return render(request, "orders/return_lookup.html", {
        "form": form,
    })


def return_detail(request, order_number):
    """
    Show the order items and let the customer select
    which ones to return / exchange.
    """
    order = get_object_or_404(Order, order_number=order_number)

    if not order.is_returnable():
        messages.error(
            request,
            "This order is not eligible for return or exchange "
            "(it must be delivered and within the return window)."
        )
        return redirect("orders:return_lookup")

    # Items that still have remaining quantity that can be returned
    items = order.items.all()

    if request.method == "POST":
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data["reason"]

            selected_items = []
            for item in items:
                qty_key = f"qty_{item.id}"
                type_key = f"type_{item.id}"

                qty = request.POST.get(qty_key)
                req_type = request.POST.get(type_key, "return")

                if qty and int(qty) > 0:
                    qty = int(qty)
                    if qty > item.quantity:
                        messages.error(request, f"Invalid quantity for {item.product_name}.")
                        return redirect("orders:return_detail", order_number=order.order_number)

                    selected_items.append({
                        "order_item": item,
                        "quantity": qty,
                        "request_type": req_type,
                    })

            if not selected_items:
                messages.error(request, "Please select at least one item to return or exchange.")
                return redirect("orders:return_detail", order_number=order.order_number)

            # Create the return request
            with transaction.atomic():
                return_req = ReturnRequest.objects.create(
                    order=order,
                    reason=reason,
                    status=ReturnRequest.Status.PENDING,
                )
                for sel in selected_items:
                    ReturnRequestItem.objects.create(
                        return_request=return_req,
                        order_item=sel["order_item"],
                        quantity=sel["quantity"],
                        request_type=sel["request_type"],
                    )

            # Notify admin (we will add the email function next)
            try:
                from .utils import send_return_request_email
                send_return_request_email(return_req)
            except Exception as e:
                print(f"Return request email failed: {e}")

            messages.success(
                request,
                "Your return / exchange request has been submitted. "
                "Our team will review it shortly."
            )
            return redirect("orders:return_detail", order_number=order.order_number)
    else:
        form = ReturnRequestForm()

    context = {
        "order": order,
        "items": items,
        "form": form,
        "is_returnable": order.is_returnable(),
    }
    return render(request, "orders/return_detail.html", context)