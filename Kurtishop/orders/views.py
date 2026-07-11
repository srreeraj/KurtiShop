from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from cart.models import Cart
from .models import Order
from .forms import OrderForm
from .services import create_order_from_cart
from .utils import create_razorpay_order

# Create your views here.

def checkout(request):
    session_key = request.session.session_key
    cart = get_object_or_404(Cart, session_key=session_key)

    if not cart.items.exists():
        return redirect('cart:cart')


    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order_data = form.cleaned_data
            subtotal = sum(item.total_price for item in cart.items.all())

            order = create_order_from_cart(cart, {
                **order_data,
                'subtotal' : subtotal,
                'grand_total' : subtotal,
            })
            # Create Razorpay Order
            razorpay_order = create_razorpay_order(
                amount_in_paisa=int(order.grand_total * 100)
            )
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            context = {
                'order' : order,
                'razorpay_key' : 'settings.RAZORPAY_KEY_ID',
                'razorpay_order_id' : razorpay_order['id'],
                'amount' : int(order.grand_total * 100) 
            }

            return render(request, 'orders/payment_page.html', context)

    else:
        form = OrderForm()

    context = {'form' : form , 'cart' : cart}
    return render(request, 'orders/checkout.html', context)

def payment_success(request):
    razorpay_payment_id = request.GET.get('razorpay_payment_id')
    razorpay_order_id = request.GET.get('razorpay_order_id')

    order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
    order.payment_status = Order.PaymentStatus.PAID
    order.razorpay_payment_id = razorpay_payment_id
    order.order_status = Order.OrderStatus.CONFIRMED
    order.save()

    return redirect('orders:order_success', 'order_number'=order.order_number)

def payment_failed(request):
    return render(request, 'orders/payment_failed.html')


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_detail.html', {'order': order})

