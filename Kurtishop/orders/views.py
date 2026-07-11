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

    form = OrderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        order_data = form.cleaned_data
        order_data.update({
            "subtotal" : sum(item.total_price for item in cart.items.all()),
            "grand_total" : sum(item.total_price for item in cart.items.all()),
        })

        order = create_order_from_cart(cart, order_data)

        # Create Razorpay Order
        razorypay_order = create_razorpay_order(int(order.grand_total * 100))
        order.razorpay_order_id = razorpay_order['id']
        order.save()

        context = {
            'order' : order,
            'razorpay_key' : 'settings.RAZORPAY_KEY_ID',
            'razorpay_order_id' : razorpay_order['id'],
            'amount' : int(order.grand_total * 100) 
        }

        return render(request, 'orders/payment_page.html', context)

    context = {'form' : form , 'cart' : cart}
    return render(request, 'orders/checkout.html', context)

