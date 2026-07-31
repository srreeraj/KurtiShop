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


class OrderLookupForm(forms.Form):
    order_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class" : INPUT_CLASSES,
            "placeholder" : "Order number (e.g. ORD-A1B2C3D4)"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Email used at checkout",
        })
    )

    def clean_order_number(self):
        return self.cleaned_data["order_number"].strip().upper()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

class OrderCancellationForm(forms.Form):
    order_number = forms.CharField(widget=forms.HiddenInput())
    email = forms.CharField(widget=forms.HiddenInput())
    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "rows": 4,
            "placeholder": "Tell us why you'd like to cancel this order...",
        })
    )

class ReturnLookupForm(forms.Form):
    order_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Order number (e.g. ORD-A1B2C3D4)"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": INPUT_CLASSES,
            "placeholder": "Email used at checkout",
        })
    )

    def clean_order_number(self):
        return self.cleaned_data["order_number"].strip().upper()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class ReturnRequestForm(forms.Form):
    """
    Dynamic form – we build the item fields in the view
    based on the order's items.
    """
    reason = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            "class": TEXTAREA_CLASSES,
            "rows": 4,
            "placeholder": "Please tell us why you want to return / exchange these items...",
        })
    )