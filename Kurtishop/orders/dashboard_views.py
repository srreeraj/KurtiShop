from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction

from .models import Order, OrderStatusHistory
from .dashboard_forms import OrderStatusUpdateForm


def get_order_context(request, per_page=15):
    qs = Order.objects.all().order_by("-created_at")

    search = request.GET.get("search", "").strip()
    if search:
        qs = qs.filter(
            Q(order_number__icontains=search) |
            Q(full_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )

    order_status = request.GET.get("order_status")
    if order_status:
        qs = qs.filter(order_status=order_status)

    payment_status = request.GET.get("payment_status")
    if payment_status:
        qs = qs.filter(payment_status=payment_status)

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    if date_from:
        qs = qs.filter(created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(created_at__date__lte=date_to)

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {
        "orders": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "search": search,
        "order_status": order_status,
        "payment_status": payment_status,
        "date_from": date_from or "",
        "date_to": date_to or "",
        "order_status_choices": Order.OrderStatus.choices,
        "payment_status_choices": Order.PaymentStatus.choices,
    }


@login_required
@user_passes_test(lambda u: u.is_staff)
def order_list(request):
    context = get_order_context(request)
    context["page_title"] = "Orders"
    return render(request, "dashboard/orders/list.html", context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def order_detail(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

    if request.method == "POST":
        form = OrderStatusUpdateForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data["order_status"]
            note = form.cleaned_data["note"]

            if new_status != order.order_status:
                with transaction.atomic():
                    order.order_status = new_status
                    order.save(update_fields=["order_status", "updated_at"])
                    OrderStatusHistory.objects.create(
                        order=order, status=new_status, note=note,
                    )
                messages.success(request, f"Order status updated to {order.get_order_status_display()}.")
            else:
                messages.info(request, "Status unchanged — no update made.")
            return redirect("orders_dashboard:order_detail", order_number=order.order_number)
    else:
        form = OrderStatusUpdateForm(initial={"order_status": order.order_status})

    items = order.items.select_related("variant__product", "variant__color", "variant__size")
    history = order.status_history.all()

    return render(request, "dashboard/orders/detail.html", {
        "order": order,
        "items": items,
        "history": history,
        "form": form,
        "page_title": f"Order {order.order_number}",
    })