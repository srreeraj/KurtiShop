from django import forms
from .models import Order

# Add this __init__ to your existing OrderForm in orders/forms.py
# This only adds CSS classes to widgets — no business logic, no field changes.

INPUT_CLASSES = (
    "w-full h-12 px-4 rounded-xl border border-gray-300 text-gray-900 "
    "placeholder-gray-400 focus:outline-none focus:border-red-600 "
    "focus:ring-2 focus:ring-red-100 transition-all duration-200"
)

TEXTAREA_CLASSES = (
    "w-full px-4 py-3 rounded-xl border border-gray-300 text-gray-900 "
    "placeholder-gray-400 focus:outline-none focus:border-red-600 "
    "focus:ring-2 focus:ring-red-100 transition-all duration-200"
)


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name", "email", "phone",
            "address_line_1", "address_line_2",
            "city", "state", "postal_code", "country",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == "notes":
                field.widget.attrs.update({
                    "class": TEXTAREA_CLASSES,
                    "rows": 4,
                    "placeholder": "Delivery instructions (optional)",
                })
            else:
                field.widget.attrs.update({
                    "class": INPUT_CLASSES,
                    "placeholder": field.label,
                })