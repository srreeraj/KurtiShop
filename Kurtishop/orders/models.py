from django.db import models
from products.models import ProductVariant
import uuid
from django.core.validators import MinValueValidator
from django.utils import timezone
from datetime import timedelta
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
# Create your models here.

invoice_storage = FileSystemStorage(
    location=os.path.join(settings.MEDIA_ROOT, 'invoices'),
    base_url=settings.MEDIA_URL + 'invoices/'
)

def invoice_upload_path(instance, filename):
    return f"{instance.order_number}/{filename}"

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
        CANCELLATION_REQUESTED = "cancellation_requested", "Cancellation Requested"
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
        max_length=30,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Current field (can be used for coupon discount later)
    discount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        help_text="Coupon or flat discount"
    )

    # NEW: Recommended field
    total_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total discount from all product variants (MRP - Selling Price)"
    )

    shipping_charge = models.DecimalField(
        max_digits=12,
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

    delivered_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    invoice  = models.FileField(
        upload_to=invoice_upload_path,
        storage=invoice_storage,
        blank=True,
        null=True,
        help_text="Generated PDF invoice"
    )

    CANCELLATION_WINDOW_DAYS = 7

    def is_cancellable(self):
        """Whether  a guest currently request cancellation """
        if self.order_status in [
            self.OrderStatus.CANCELLED,
            self.OrderStatus.CANCELLATION_REQUESTED,
        ]:
            return False

        if self.order_status == self.OrderStatus.SHIPPED:
            # Already handed to courier — block cancellation until delivered
            return False

        if self.order_status == self.OrderStatus.DELIVERED:
            if not self.delivered_at:
                return False
            return timezone.now() <= self.delivered_at + timedelta(days=self.CANCELLATION_WINDOW_DAYS)

        # pending / confirmed / processing
        return True

    def cancellation_deadline(self):
        """Returns the deadline datetime if order is delivered, else None."""
        if self.order_status == self.OrderStatus.DELIVERED and self.delivered_at:
            return self.delivered_at + timedelta(days=self.CANCELLATION_WINDOW_DAYS)
        return None

    def get_pre_cancellation_status(self):
        """Best-guess status to revert to if admin rejects the cancellation request."""
        last = (
            self.status_history
            .exclude(status=self.OrderStatus.CANCELLATION_REQUESTED)
            .order_by("-created_at")
            .first()
        )
        return last.status if last else self.OrderStatus.CONFIRMED

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["guest_session_key"]),
            models.Index(fields=["order_number"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["order_status"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            while True:
                number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
                if not Order.objects.filter(order_number=number).exists():
                    self.order_number = number
                    break
        super().save(*args, **kwargs)

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    # Reference to current variant (for stock, etc.)
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,   # Changed to SET_NULL (important!)
        null=True,
        blank=True,
        related_name="order_items"
    )

    # Snapshot fields - What customer actually bought
    product_name = models.CharField(max_length=255)
    variant_sku = models.CharField(max_length=100)
    size = models.CharField(max_length=50)
    color = models.CharField(max_length=100)

    # New : Critical for tansperency
    original_unit_price = models.DecimalField(max_digits=12, decimal_places=2) #MRP
    unit_price = models.DecimalField(
        max_digits = 12,
        decimal_places=2
    )
    discount_percentage = models.PositiveIntegerField(default=0)

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    #Per items savings
    savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} ({self.size}/{self.color})"

class OrderStatusHistory(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    status = models.CharField(
        max_length=30,
        choices=Order.OrderStatus.choices
    )

    note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order.order_number} - {self.status}"