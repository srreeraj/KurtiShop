from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product_name', 'variant_sku', 'size', 'color',
        'original_unit_price', 'unit_price', 'discount_percentage',
        'quantity', 'total_price', 'savings'
    ]
    can_delete = False


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'note', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'full_name', 'email', 'phone',
        'grand_total', 'payment_status_colored', 'order_status',
        'created_at'
    ]
    list_filter = ['payment_status', 'order_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'full_name', 'email', 'phone']
    readonly_fields = [
        'order_number', 'guest_session_key', 'razorpay_order_id',
        'razorpay_payment_id', 'created_at', 'updated_at'
    ]

    inlines = [OrderItemInline, OrderStatusHistoryInline]

    fieldsets = [
        ("Order Info", {
            'fields': ('order_number', 'guest_session_key', 'created_at', 'updated_at')
        }),
        ("Customer Details", {
            'fields': ('full_name', 'email', 'phone')
        }),
        ("Shipping Address", {
            'fields': (
                'address_line_1', 'address_line_2',
                'city', 'state', 'postal_code', 'country'
            )
        }),
        ("Pricing", {
            'fields': (
                'subtotal', 'total_discount', 'discount',
                'shipping_charge', 'tax', 'grand_total'
            )
        }),
        ("Payment & Status", {
            'fields': (
                'payment_method', 'payment_status',
                'order_status', 'razorpay_order_id', 'razorpay_payment_id'
            )
        }),
        ("Notes", {
            'fields': ('notes',)
        }),
    ]

    def payment_status_colored(self, obj):
        colors = {
            'paid': 'green',
            'pending': 'orange',
            'failed': 'red',
            'refunded': 'purple'
        }
        color = colors.get(obj.payment_status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_payment_status_display()
        )
    payment_status_colored.short_description = "Payment Status"


# Register the rest if needed
admin.site.register(OrderItem)
admin.site.register(OrderStatusHistory)