from django.contrib import admin
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    ProductAttribute,
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
    show_change_link = True
    readonly_fields = ('variant_sku',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    autocomplete_fields = ['color']
    show_change_link = True

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 0

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

    list_select_related = (
        'category',
        'material',
        'occasion',
        'pattern',
        'fit',
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

    ordering = ('name',)

    readonly_fields = (
        "sku",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Basic Information",
            {
                "fields" : (
                    "category",
                    "name",
                    "sku",
                    "slug",
                    "description"
                )
            },
        ),
        (
            "Product Details",
            {
                "fields" : (
                    "material",
                    "occasion",
                    "pattern",
                    "fit",
                    "sleeve",
                    "neck",
                    "length",
                    "yoke",
                    "back",
                    "lining",
                    "wash_care"
                )
            },
        ),
        (
            "Marketing",
            {
                "fields" : (
                    "tags",
                    "is_featured",
                    "is_new_arrival",
                )
            },
        ),
        (
            "Status",
            {
                "fields" : (
                    "is_active",
                    "is_deleted",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields" : (
                    "created_at",
                    "updated_at",
                )
            }
        )
    )

    inlines = [
        ProductVariantInline,
        ProductImageInline,
        ProductAttributeInline,
    ]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "color",
        "view",
        "display_order",
        "is_primary",
    )

    list_filter = (
        "view",
        "color",
        "is_primary",
    )

    search_fields = (
        "product__name",
    )

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "size",
        "color",
        "price",
        "stock",
    )

    list_filter = (
        "size",
        "color",
    )

    search_fields = (
        "product__name",
        "variant_sku",
    )

    readonly_fields = (
        'variant_sku',
    )

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
    list_display = ('name',)
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
    