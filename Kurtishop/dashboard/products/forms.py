from django import forms
from products.models import (
    Product, ProductVariant, ProductImage, 
    Category, Size, Color, Material, Occasion, etc.
)

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'category', 'name', 'description', 'material', 'occasion',
            'sleeve', 'neck', 'pattern', 'fit', 'length', 'yoke', 'back',
            'lining', 'wash_care', 'is_featured', 'is_new_arrival', 'is_active'
        ]
        widgets = { ... }  # same style as CategoryForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_deleted=False)


# Inline-style forms for JS
class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'price', 'discount_percentage', 'stock']


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['color', 'view', 'image', 'display_order', 'is_primary']