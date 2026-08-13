from django import forms
from django.forms import inlineformset_factory
from .models import Product, ProductVariant, ProductImage, ProductAttribute, ServiceablePincode

INPUT = "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
FILE = "block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-2xl file:border-0 file:text-sm file:font-medium file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
CHECKBOX = "w-5 h-5 rounded border-gray-300 text-red-600 focus:ring-red-500"


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category", "name", "description",
            "material", "occasion", "sleeve", "neck", "pattern", "fit",
            "length", "yoke", "back", "lining", "wash_care",
            "tags", "is_featured", "is_new_arrival", "is_active",
            "allowed_pincodes"
        ]
        widgets = {
            "category": forms.Select(attrs={"class": INPUT}),
            "name": forms.TextInput(attrs={"class": INPUT, "placeholder": "e.g. Banarasi Silk Saree"}),
            "description": forms.Textarea(attrs={"class": INPUT, "rows": 4}),
            "material": forms.Select(attrs={"class": INPUT}),
            "occasion": forms.Select(attrs={"class": INPUT}),
            "sleeve": forms.Select(attrs={"class": INPUT}),
            "neck": forms.Select(attrs={"class": INPUT}),
            "pattern": forms.Select(attrs={"class": INPUT}),
            "fit": forms.Select(attrs={"class": INPUT}),
            "length": forms.TextInput(attrs={"class": INPUT, "placeholder": "Ankle Length / 42 inches"}),
            "yoke": forms.TextInput(attrs={"class": INPUT}),
            "back": forms.TextInput(attrs={"class": INPUT}),
            "wash_care": forms.Textarea(attrs={"class": INPUT, "rows": 3}),
            "tags": forms.SelectMultiple(attrs={"class": INPUT}),
            "lining": forms.CheckboxInput(attrs={"class": CHECKBOX}),
            "is_featured": forms.CheckboxInput(attrs={"class": CHECKBOX}),
            "is_new_arrival": forms.CheckboxInput(attrs={"class": CHECKBOX}),
            "is_active": forms.CheckboxInput(attrs={"class": CHECKBOX}),
            "allowed_pincodes": forms.SelectMultiple(attrs={
                "class": INPUT + " h-40",   # taller multi-select
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ["category", "material", "occasion", "sleeve", "neck", "pattern", "fit"]:
            self.fields[f].empty_label = f"— Select {f.title()} —"
        self.fields["tags"].required = False

        # Only show active pincodes
        self.fields["allowed_pincodes"].queryset = ServiceablePincode.objects.filter(is_active=True)
        self.fields["allowed_pincodes"].help_text = (
            "Leave empty = available in all serviceable areas. "
            "Select specific pincodes to restrict this product."
        )


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ["size", "color", "price", "discount_percentage", "stock", "is_active"]
        widgets = {
            "size": forms.Select(attrs={"class": INPUT}),
            "color": forms.Select(attrs={"class": INPUT}),
            "price": forms.NumberInput(attrs={"class": INPUT, "step": "0.01", "min": "0"}),
            "discount_percentage": forms.NumberInput(attrs={"class": INPUT, "min": "0", "max": "100"}),
            "stock": forms.NumberInput(attrs={"class": INPUT, "min": "0"}),
            "is_active": forms.CheckboxInput(attrs={"class": CHECKBOX}),
        }

class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        fields = ["name", "value"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": INPUT,
                "placeholder": "e.g. Metal / Stone / Weight"
            }),
            "value": forms.TextInput(attrs={
                "class": INPUT,
                "placeholder": "e.g. Gold / Diamond / 12g"
            }),
        }


# extra=1 gives one blank row by default; JS clones more as needed.
# empty_permitted on extra forms means a row left fully blank is silently skipped.
ProductVariantFormSet = inlineformset_factory(
    Product,
    ProductVariant,
    form=ProductVariantForm,
    extra=1,
    can_delete=True,
)

ProductAttributeFormSet = inlineformset_factory(
    Product,
    ProductAttribute,
    form=ProductAttributeForm,
    extra=1,
    can_delete=True,
)