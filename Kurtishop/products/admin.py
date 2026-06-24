from django.contrib import admin
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    Size,
    Color
)
# Register your models here.

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'category',
        'is_active',
        'is_featured'
    )

    list_filter = (
        'category',
        'is_active',
        'is_featured'
    )

    search_fields = (
        'name',
        'sku'
    )

    perpopulated_fields = {
        'slug' : ('name',)
    }

    inlines = [
        ProductVariantInline,
        ProductImageInline,
    ]

admin.site.register(Size)
admin.site.register(Color)
