from django.contrib import admin
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    Size,
    Color,
    Material,
    Occasion,
    Sleeve,
    Neck,
    Pattern,
    Fit,
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
        'material',
        'is_featured',
        'is_new_arrival',
        'is_active',
    )

    list_filter = (
        'category',
        'materail',
        'occassion',
        'is_featured',
        'is_new_arrival',
        'is_active',
    )

    search_fields = (
        'name',
        'sku',
        'description',
    )

    prepopulated_fields = {
        'slug' : ('name',)
    }

    inlines = [
        ProductVariantInline,
        ProductImageInline,
    ]

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Sleeve)
class SleeveAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Neck)
class NeckAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Fit)
class FitAdmin(admin.ModelAdmin):
    search_fields = ('name',)