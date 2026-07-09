from django.http import HttpRequest
from .models import Cart
from django.db.models import Sum

def get_or_create_cart(request: HttpRequest):
    """Get or create a cart for the current session."""
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def get_cart_item_count(request: HttpRequest):
    """For showing the count in navbar"""
    cart = get_or_create_cart(request)
    return cart.items.aggregate(
        total=Sum("quantity")
    )["total"] or 0