from django.db import transaction
from .models import Order, OrderItem
from products.models import ProductVariant
from cart.models import Cart
from django.template.loader import render_to_string
from django.conf import settings
import logging
from django.utils import timezone
from decimal import Decimal
from .models import ReturnRequest, ReturnRequestItem, OrderItem, OrderStatusHistory

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
def clear_cart_after_order(order):
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

@transaction.atomic
def fulfill_exchange_request(return_req, items_data, admin_user=None):
    """
    items_data = [
        {
            "return_item_id": 12,
            "new_variant": <ProductVariant instance>,
            "new_quantity": 1,
        },
        ...
    ]
    """
    order = return_req.order
    total_price_diff = Decimal("0.00")

    for data in items_data:
        ritem = ReturnRequestItem.objects.select_for_update().get(
            id=data["return_item_id"],
            return_request=return_req,
            request_type=ReturnRequest.RequestType.EXCHANGE,
        )
        old_item = ritem.order_item
        new_variant = data["new_variant"]
        new_qty = data["new_quantity"]

        # ---------- Stock adjustments ----------
        # 1. Restore stock of original variant
        if old_item.variant_id:
            old_variant = ProductVariant.objects.select_for_update().get(
                id=old_item.variant_id
            )
            old_variant.stock += ritem.quantity
            old_variant.save(update_fields=["stock"])

        # 2. Deduct stock of new variant
        new_variant = ProductVariant.objects.select_for_update().get(id=new_variant.id)
        if new_variant.stock < new_qty:
            raise ValueError(
                f"Insufficient stock for {new_variant} "
                f"(needed {new_qty}, available {new_variant.stock})"
            )
        new_variant.stock -= new_qty
        new_variant.save(update_fields=["stock"])

        # ---------- Price calculation ----------
        old_line_total = old_item.unit_price * ritem.quantity
        new_unit_price = new_variant.discounted_price
        new_line_total = new_unit_price * new_qty
        price_diff = new_line_total - old_line_total
        total_price_diff += price_diff

        # ---------- Update OrderItem in-place (simplest for guest system) ----------
        old_item.variant = new_variant
        old_item.product_name = new_variant.product.name
        old_item.variant_sku = new_variant.variant_sku
        old_item.size = new_variant.size.name
        old_item.color = new_variant.color.name
        old_item.original_unit_price = new_variant.price
        old_item.unit_price = new_unit_price
        old_item.discount_percentage = new_variant.discount_percentage
        old_item.quantity = new_qty
        old_item.total_price = new_line_total
        old_item.savings = (new_variant.price - new_unit_price) * new_qty
        old_item.save()

        # ---------- Snapshot on ReturnRequestItem ----------
        ritem.exchanged_to_variant = new_variant
        ritem.new_product_name = new_variant.product.name
        ritem.new_variant_sku = new_variant.variant_sku
        ritem.new_size = new_variant.size.name
        ritem.new_color = new_variant.color.name
        ritem.new_unit_price = new_unit_price
        ritem.new_quantity = new_qty
        ritem.price_difference = price_diff
        ritem.fulfilled_at = timezone.now()
        ritem.save()

    # ---------- Recalculate order totals ----------
    items = order.items.all()
    subtotal = sum(i.total_price for i in items)
    total_discount = sum(i.savings for i in items)

    order.subtotal = subtotal
    order.total_discount = total_discount
    order.grand_total = (
        subtotal + order.shipping_charge + order.tax - order.discount
    )
    order.save(update_fields=[
        "subtotal", "total_discount", "grand_total", "updated_at"
    ])

    # ---------- Mark request as fulfilled ----------
    return_req.status = getattr(
        ReturnRequest.Status, "FULFILLED", ReturnRequest.Status.COMPLETED
    )
    return_req.save(update_fields=["status", "updated_at"])

    # ---------- History note ----------
    note = "Exchange fulfilled by admin."
    if total_price_diff != 0:
        note += f" Price difference: ₹{total_price_diff}"
    OrderStatusHistory.objects.create(
        order=order,
        status=order.order_status,
        note=note,
    )

    return total_price_diff