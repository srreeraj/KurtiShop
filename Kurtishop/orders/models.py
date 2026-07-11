from django.db import models
from django.utils.timezone import now
from products.models import ProductVariant
from decimal import Decimal
import uuid
# Create your models here.
class Order(models.Model):

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash On Delivery"
        ONLINE = "online", "Online Payment"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded","Refunded"

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    order_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
    )

    guest_session_key = models.CharField(max_length=40, db_index=True) # from cart session
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    country = models.CharField(max_length=100, default="India")

    postal_code = models.CharField(max_length=20)

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.ONLINE,
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )

    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    shipping_charge = models.DecimalField(
        max_digit=12,
        decimal_places=2,
        default=0
    )

    tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    grand_total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["guest_session_key"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["payments_status"]),
            models.Index(fields=["order_status"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    varaint = models.ForeignKey(
        ProductVariant,
        on_delete = models.PROTECT,
        related_name="order_items"
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits = 12,
        decimal_places=2
    )

    discount_percentage = models.PositiveIntegerField(default=0)

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.order.order_number} - {self.variant}"

class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(max_length=50)

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)