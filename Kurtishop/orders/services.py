from django.db import transaction
from .models import Order, OrderItem
from products.models import ProductVariant
from cart.models import Cart
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


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
    return order

@transaction.atomic
def clear_cart_after_order(cart):
    """
    Safely clear the cart that belongs to this order.
    Called only after payment is confirmed.
    Idempotent : safe to call multiple times.
    """

    if not order.guest_session_key:
        return
    
    deleted_count, _ = Cart.objects.filter(session_key=order.guest_session_key).delete()

    if deleted_count:
        logger.info(
            "Cart cleared after order %s (session_key=%s)",
            order.order_number,
            order.guest_session_key,
        )

@transaction.atomic
def deduct_stock_after_payment(order):
    """
        Deduct stock only after successful payment,
        This is atomic to prevent overselling
    """
    items = list(order.items.select_related('variant').all())

    # Collect only existing variant IDs
    variant_ids = [item.variant_id for item in items if item.variant_id]

    if not variant_ids:
        return

    # Lock the actual ProductVariant rows (this is the correct & safe way)
    locked_variants = {
        v.id: v
        for v in ProductVariant.objects.select_for_update().filter(id__in=variant_ids)
    }
    
    for item in items:
        if not item.variant_id:
            continue

        variant = locked_variants.get(item.variant_id)
        if not variant:
            logger.warning(
                "Variant %s not found while deducting stock for order %s",
                item.variant_id,
                order.order_number,
            )
            continue

        if variant.stock < item.quantity:
            raise ValueError(
                f"Insufficient stock for {variant} "
                f"(needed {item.quantity}, available {variant.stock})"
            )

        variant.stock -= item.quantity
        variant.save(update_fields=['stock'])

    # Update order status only if it is still in a pre-confirmation state
    if order.order_status in (
        Order.OrderStatus.PENDING,
        getattr(Order.OrderStatus, 'AWAITING_PAYMENT', None),
    ):
        order.order_status = Order.OrderStatus.CONFIRMED
        order.save(update_fields=['order_status', 'updated_at'])