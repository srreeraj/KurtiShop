from django.db import models
from django.utils.text import slugify
from decimal import Decimal
import os

from categories.models import Category
# Create your models here.

# Lookup models

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

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Occasion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Sleeve(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Neck(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Pattern(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Fit(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class ProductTag(models.Model):
    name = models.CharField(
        max_length=150,
        unique=True,
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products'
    )

    tags = models.ManyToManyField(
        ProductTag,
        blank=True,
        related_name='products'
    )
    
    material = models.ForeignKey(
        Material,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    occasion = models.ForeignKey(
        Occasion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    sleeve = models.ForeignKey(
        Sleeve,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    neck = models.ForeignKey(
        Neck,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    pattern = models.ForeignKey(
        Pattern,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    fit = models.ForeignKey(
        Fit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True, blank=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)

    description = models.TextField(blank=True)

    length = models.CharField(
        max_length=100,
        blank=True,
        help_text="Ankle Length, Calf Length, 100 cm, 42 inches"
    )

    yoke = models.CharField(
        max_length=150,
        blank=True
    )

    back = models.CharField(
        max_length=150,
        blank=True,
    )

    lining = models.BooleanField(default=False)

    wash_care = models.TextField(blank=True, null=True)

    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_featured"]),
            models.Index(fields=["is_new_arrival"]),
        ]

    def save(self, *args, **kwargs):

        # SKU auto generation
        if not self.sku:
            last_product = Product.objects.order_by('-id').first()

            if last_product:
                last_number = int(last_product.sku[-6:])
                next_number = last_number + 1
            else:
                next_number = 1

            #should update the after getting real name
            self.sku = f"WMS{next_number:06d}"

        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)

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

    variant_sku = models.CharField(max_length=100, unique=True, blank=True)

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

        ordering = [
            "size",
            "color",
        ]

    @property
    def discounted_price(self):
        return self.price - (
            self.price * Decimal(self.discount_percentage) / Decimal('100')
        )

    def save(self, *args, **kwargs):
        if not self.variant_sku:
            self.variant_sku = (
                f"{self.product.sku}-"
                f"{self.size.name.upper()}-"
                f"{slugify(self.color.name).upper()}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.product.name} - "
            f"{self.size.name} - "
            f"{self.color.name}"
        )

def product_image_upload_path(instance, filename):
    """
    Upload path :
    products/<category>/<product>/<color>/<view>.<extension>
    """

    extension = filename.split('.')[-1]

    category = slugify(instance.product.category.name)
    product = slugify(instance.product.name)
    color = slugify(instance.color.name)

    filename = f"{instance.view}.{extension}"

    return os.path.join(
        "products",
        category,
        product,
        color,
        filename
    )

class ProductImage(models.Model):

    class ImageView(models.TextChoices):
        FRONT = "front","Front"
        BACK = "back", "Back"
        LEFT = "left", 'Left Side'
        RIGHT = "right", 'Right Side'
        THREE_QUARTER = "three-quarter", "3/4 View"
        CLOSEUP = "closeup", "Close Up"
        DETAIL = "detail", "Detail"


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

    view = models.CharField(
        max_length=50,
        choices=ImageView.choices,
        default=ImageView.FRONT,
    )

    image = models.ImageField(
        upload_to=product_image_upload_path
    )

    alt_text = models.CharField(
        max_length=255,
        blank=True,
    )

    display_order = models.PositiveIntegerField(
        default=1
    )

    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = [
            "display_order",
            "view",
            ]

        constraints = [
            models.UniqueConstraint(
                fields=['product','color','view'],
                name="unique_product_color_view"
            )
        ]

    def save(self, *args, **kwargs):

        if not self.alt_text:
            self.alt_text = (
                f"{self.product.name} - "
                f"{self.color.name} - "
                f"{self.get_view_display()}"
            )
        
        super().save(*args, **kwargs)

    def __str__(self):
        return ( 
            f"{self.product.name} - "
            f"{self.color.name} - "
            f"{self.get_view_display()}"
        )

class ProductAttribute(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes'
    )

    name = models.CharField(max_length = 100)
    value = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} : {self.value}"