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