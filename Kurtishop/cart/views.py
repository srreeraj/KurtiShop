from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages

from products.models import ProductVariant
from .models import Cart, CartItem
from .utils import get_or_create_cart, get_cart_item_count

# Create your views here.


def cart_drawer(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related(
        'variant__product',
        'variant__color', 
        'variant__size'
    ).prefetch_related(
        'variant__product__images'
    ).all()
    
    subtotal = sum(item.total_price for item in items)

    return render(request, 'cart/cart_drawer.html', {
        'items': items,
        'subtotal': subtotal,
    })

@require_POST
def add_to_cart(request, variant_id):
    cart = get_or_create_cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)

    quantity = int(request.POST.get('quantity', 1))

    if quantity < 1:
        return JsonResponse({'status' : 'error' , 'message' : 'Invalid quantity'}, status=404)

    # Stock check
    if quantity > variant.stock:
        return JsonResponse({
            'status' : 'error',
            'message' : f'Only {variant.stock} items available in stock'
        }, status=400)

    # Add or update items
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            'quantity': quantity,
            'original_unit_price': variant.price,
            'unit_price': variant.discounted_price,
            'discount_percentage': variant.discount_percentage,
            'savings': (variant.price - variant.discounted_price) * quantity,
            'product_name': variant.product.name,
        }
    )

    if not created:
        new_qty = cart_item.quantity + quantity
        if new_qty > variant.stock:
            return JsonResponse({
                'status' : 'error',
                'message' : 'Not enough stock',
            }, status=404)
        cart_item.quantity = new_qty
        cart_item.savings = (variant.price - variant.discounted_price) * new_qty
        cart_item.save()

    return JsonResponse({
        'status' : 'success',
        'message' : f'{quantity} x {variant.product.name} added to cart',
        'cart_count' : cart.items.count()
    })

@require_POST
def remove_from_cart(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return JsonResponse({
        "status" : "success"
    })

@require_POST
def update_cart_quantity(request, item_id):
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        change = int(request.POST.get('quantity', 0))
    except (ValueError, TypeError):
        return JsonResponse({
            "status": "error",
            "message": "Invalid quantity",
        }, status=400)

    new_quantity = cart_item.quantity + change

    if new_quantity < 1:
        cart_item.delete()
        return JsonResponse({"status": "success"})

    if new_quantity > cart_item.variant.stock:
        return JsonResponse({
            "status": "error",
            "message": f"Only {cart_item.variant.stock} item(s) available."
        }, status=400)

    cart_item.quantity = new_quantity
    cart_item.save()

    return JsonResponse({"status": "success"})