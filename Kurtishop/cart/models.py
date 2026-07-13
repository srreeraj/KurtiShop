from django.db import models
from products.models import ProductVariant
# Create your models here.

class Cart(models.Model):
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Cart  {self.session_key}"

    
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'variant'],
                name='unique_cart_item'
            )
        ]

    @property
    def unit_price(self):
        return self.variant.discounted_price

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    @property
    def image_url(self):
        """Return the best image for this variant's color"""
        image = self.variant.product.images.filter(
            color=self.variant.color,
            is_primary=True
        ).first()

        if not image:
            image = self.variant.product.images.filter(
                color=self.variant.color
            ).order_by('display_order').first()

        return image.image.url if image else None

        
    def __str__(self):
        return (
            f"{self.variant.product.name} - "
            f"({self.variant.color.name} / {self.variant.size.name}) - "
            f"x {self.quantity}"
        )