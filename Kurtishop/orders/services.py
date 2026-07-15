from django.db import transaction
from .models import Order, OrderItem
from cart.models import Cart


@transaction.atomic
def create_order_from_cart(cart, form_data):
    """
    Create order from cart with full price transparency (MRP + Discounted Price + Savings)
    """
    # form_data should contain: full_name, email, phone, address..., subtotal, grand_total, etc.
    
    order = Order.objects.create(
        guest_session_key=cart.session_key,
        **form_data
    )

    total_discount = 0

    for cart_item in cart.items.select_related('variant__product', 'variant__size', 'variant__color').all():
        variant = cart_item.variant
        
        # === Pricing Calculations ===
        original_price = variant.price                     # MRP
        selling_price = variant.discounted_price           # After discount
        discount_pct = variant.discount_percentage
        
        savings_per_unit = original_price - selling_price
        line_savings = savings_per_unit * cart_item.quantity
        line_total = selling_price * cart_item.quantity

        total_discount += line_savings

        OrderItem.objects.create(
            order=order,
            
            # Reference
            variant=variant,
            
            # Snapshot data (for historical accuracy)
            product_name=variant.product.name,
            variant_sku=variant.variant_sku,
            size=variant.size.name,
            color=variant.color.name,
            
            # === Pricing Fields ===
            original_unit_price=original_price,      # NEW
            unit_price=selling_price,                # Selling price
            discount_percentage=discount_pct,
            quantity=cart_item.quantity,
            total_price=line_total,                  # Final payable for this line
            savings=line_savings,                    # NEW - Important for UI
        )

    # Update Order with total discount (recommended)
    order.total_discount = total_discount
    order.save()

    # Clear cart
    cart.items.all().delete()
    cart.delete()

    return order