from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart


@transaction.atomic
def create_order_from_cart(cart, form_data):
    order = Order.objects.create(
        guest_session_key=cart.session_key,
        **form_data
    )

    for cart_item in cart.items.all():
        variant = cart_item.variant
        OrderItem.objects.create(
            order=order,
            variant=variant,
            quantity=cart_item.quantity,
            unit_price=variant.discounted_price,
            discount_percentage=variant.discount_percentage,
            total_price=cart_item.total_price,
        )

    # Clear cart after order creation
    cart.items.all().delete()
    cart.delete()

    return order