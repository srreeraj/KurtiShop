from django.contrib import admin
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductTag,
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
    autocomplete_fields = ['size','color']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    autocomplete_fields = ['color']

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

    filter_horizontal = (
        'tags',
    )

    list_filter = (
        'category',
        'material',
        'occasion',
        'pattern',
        'fit',
        'is_featured',
        'is_new_arrival',
        'is_active',
    )

    search_fields = (
        'name',
        'sku',
        'description',
        'material__name',
        'occasion__name',
        'category__name',
    )

    prepopulated_fields = {
        'slug' : ('name',)
    }

    inlines = [
        ProductVariantInline,
        ProductImageInline,
    ]

    ordering = ('name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Occasion)
class OccasionAdmin(admin.ModelAdmin):
    list_dispaly = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Sleeve)
class SleeveAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Neck)
class NeckAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Pattern)
class PatternAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Fit)
class FitAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    