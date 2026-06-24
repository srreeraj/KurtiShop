from django.db import models
from django.utils.text import slugify
from decimal import Decimal

from categories.models import Category
# Create your models here.

class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    description = models.TextField(blank=True)

    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(
        max_length=10,
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
    )

    class Meta:
        ordering = ['name']
    def __str__(self):
        return self.name

class ProductVariant(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants'
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE
    )

    variant_sku = models.CharField(max_length=100, unique=True)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_percentage = models.PositiveIntegerField(
        default=0
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(default=True)

    is_deleted = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['product','size','color'],
                name='unique_product_variant'
            )
        ]

    @property
    def discounted_price(self):
        return self.price - (
            self.price * Decimal(self.discount_percentage) / Decimal('100')
        )

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.size.name} - "
            f"{self.color.name}"
        )

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(
        upload_to='products/'
    )

    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return ( 
            f"{self.product.name} - "
             f"{self.color.name}"
        )