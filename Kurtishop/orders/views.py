from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from cart.models import Cart
from .models import Order
from .forms import OrderForm
from .services import create_order_from_cart

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

    sub_total = sum(item.total_price for item in items)

    discount = 0
    shipping = 0
    tax = 0
    grand_total = subtotal + shipping + tax - discount


    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = form.cleaned_data
            subtotal = sum(item.total_price for item in cart.items.all())

            order = create_order_from_cart(cart, {
                **order_data,
                'subtotal': subtotal,
                'discount': discount,
                'shipping_charge': shipping,
                'tax': tax,
                'grand_total': grand_total,
                'payment_method': 'online',
            })

            return render(request, 'orders/payment_page.html',order_number=order.order_number)

    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart': cart,
        'items': items,
        'subtotal': subtotal,
        'discount': discount,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'show_button': True,
        'button_text': 'Proceed to Secure Payment',
    }
    
    return render(request, 'orders/checkout.html', context)


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_detail.html', {'order': order})

