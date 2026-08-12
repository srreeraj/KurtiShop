from django import forms
from .models import Order

INPUT = "block w-full rounded-2xl border-gray-200 focus:border-red-500 focus:ring-red-500 py-3 px-4"
TEXTAREA = INPUT


class OrderStatusUpdateForm(forms.Form):
    """Admin-only: change order_status and optionally leave a note.
    payment_status is intentionally NOT included here — it stays
    automated via the Razorpay webhook / payment flow."""

    order_status = forms.ChoiceField(
        choices=Order.OrderStatus.choices,
        widget=forms.Select(attrs={"class": INPUT}),
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": TEXTAREA, "rows": 2,
            "placeholder": "Optional note (e.g. tracking number, reason for cancellation)",
        }),
    )

class ExchangeFulfillItemForm(forms.Form):
    """One form per ReturnRequestItem that needs exchange."""

    def __init__(self, *args, return_item=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.return_item = return_item

        # Only variants of the same product (common case)
        product = None
        if return_item and return_item.order_item.variant:
            product = return_item.order_item.variant.product

        if product:
            qs = ProductVariant.objects.filter(
                product=product,
                is_active=True,          # adjust if your field name is different
            ).select_related("size", "color").order_by("size__name", "color__name")
        else:
            qs = ProductVariant.objects.none()

        self.fields["new_variant"] = forms.ModelChoiceField(
            queryset=qs,
            empty_label="Select new size / color",
            widget=forms.Select(attrs={
                "class": "w-full rounded-xl border-gray-200 text-sm py-2 px-3"
            }),
            label="New variant",
        )
        self.fields["new_quantity"] = forms.IntegerField(
            min_value=1,
            initial=return_item.quantity if return_item else 1,
            widget=forms.NumberInput(attrs={
                "class": "w-24 rounded-xl border-gray-200 text-sm py-2 px-3",
                "min": 1,
            }),
        )